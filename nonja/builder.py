import json
import sys
import importlib
import lxml.etree as et
from os import path, walk, getcwd, makedirs, system, unlink
from jinja2 import Environment, FileSystemLoader
from lxml.builder import E
from datetime import datetime
from json import load
import shutil
from PIL import Image

from nonja.style import bold, reset
import nonja.console as console
import nonja.filters as filters
import nonja.functions as functions


def _run_package_manager():
    # TODO: Feels like there might be a better manner of handling invoking the package manager.
    npm_lock_path = "./package-lock.json"
    yarn_lock_path = "./yarn.lock"

    if path.exists(npm_lock_path):
        system("npm run sass:build")
    elif path.exists(yarn_lock_path):
        system("yarn sass:build")
    elif not path.exists(npm_lock_path) and not path.exists(yarn_lock_path):
        console.error("Package lock files could not be found, ignoring.")


def rebuild_project():
    # TODO: Need to use file removal methods from Python instead of this.
    build_folder_path = path.join(".", "build")
    system(f"rm -rf {build_folder_path}")
    build_project()


def build_project(**args):
    project_config = _get_project_config()
    _run_package_manager()

    include_assets_flag = "include-assets"

    if include_assets_flag in args and args.get(include_assets_flag):
        _migrate_assets()

    content_folder_path = path.join(getcwd(), "src/content")
    if not path.exists(content_folder_path):
        console.error(f"Content source path {bold}{content_folder_path}{reset} could not be found")
        exit(0)
    else:
        console.info(f"Processing content from folder {bold}{content_folder_path}{reset}")

    x_filter_mod_name = path.join(getcwd(), "filters.py")
    if path.exists(x_filter_mod_name):
        sys.path.insert(0, getcwd())

    console.info("Setting up Jinja environment.")
    env = Environment(
        loader=FileSystemLoader(content_folder_path),
        autoescape=False
    )

    env.filters = {
        "date": filters.datetime_format,
        "encode": filters.encode,
    }

    try:
        x_filter_mod_name = "filters"
        x_filter_mod = importlib.import_module(x_filter_mod_name)
        for f in dir(x_filter_mod):
            if not f.startswith("__") and not f.startswith("_"):
                env.filters[f] = getattr(x_filter_mod, f)
    except ImportError:
        pass

    env.globals.update(
        path_for=functions.path_for,
        site=functions.site,
        data=functions.import_json,
        markdown=functions.import_markdown,
    )

    source_folder_path = "src/content"
    build_target_path = "build"

    build_tally = 0

    for cwd, _, files in walk(content_folder_path):
        for file in files:
            if file.startswith("_") or not file.endswith(".j2"):
                continue

            content_file_path = path.join(cwd.replace(content_folder_path, ""), file)
            if content_file_path.startswith("/"):
                content_file_path = content_file_path[1:]

            template = env.get_template(content_file_path)
            result = template.render()

            output_file_path = path.join(cwd, f"{file}").replace(source_folder_path, build_target_path)
            output_folder_path = path.dirname(output_file_path)

            if not path.exists(output_folder_path):
                makedirs(output_folder_path, exist_ok=True)

            with open(output_file_path, "wb") as output_file:
                output_file.write(result.encode())
                build_tally += 1

    console.info(f"Wrote {bold}{build_tally}{reset} pages for the project.")

    _write_robots_file()
    _write_sitemap()


def _write_sitemap():
    package_file_path = path.join(getcwd(), "package.json")
    with open(package_file_path, "rb") as package_file:
        package_content = json.load(package_file)

    project_config = package_content.get("nonjaProject")
    project_base_url = project_config.get("domain")

    build_folder_path = path.join(getcwd(), "build")
    sitemap_node_count = 0
    sitemap_content = E.sitemap(
        {
            "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }
    )
    for cwd, _, files in walk(build_folder_path):
        for filename in files:
            if not filename.endswith(".html"):
                continue

            file_path = (path.join(cwd, filename)
                         .replace(path.join(getcwd(), "build"), project_base_url)
                         .replace("index.html", ""))

            sitemap_content.append(E.url(
                E.loc(file_path),
                E.lastmod(datetime.now().strftime("%Y-%m-%d"))
            ))
            sitemap_node_count += 1

    sitemap_file_path = path.join(getcwd(), "build/sitemap.xml")
    with open(sitemap_file_path, "wb") as sitemap_file:
        sitemap_file.write(et.tostring(sitemap_content, pretty_print=True))

    console.info(f"Wrote site map data file {bold}{sitemap_file_path}{reset} for {sitemap_node_count} url nodes")


def _write_robots_file():
    # Create robots.txt
    robots_file_content = """# www.robotstxt.org/

# Allow crawling for all content
User-agent: *
Disallow:
"""
    robots_file_path = "./build/robots.txt"
    with open(robots_file_path, "wb") as robots_file:
        robots_file.write(robots_file_content.encode())

    console.info(f"Wrote {bold}robots.txt{reset} for the project.")


def _get_project_config():
    package_file_path = path.join(getcwd(), "package.json")
    with open(package_file_path, "rb") as package_file:
        package_content = load(package_file)

    return package_content.get("nonjaProject", None)

def _migrate_assets():
    image_assets_path = "./src/images"
    image_assets_folder = path.join(getcwd(), image_assets_path)
    output_image_path = "./build/assets/images"
    output_image_folder = path.join(getcwd(), output_image_path)

    drawings_assets_path = "./src/drawings"
    drawings_assets_folder = path.join(getcwd(), drawings_assets_path)
    output_drawings_path = "./build/assets/drawings"
    output_drawings_folder = path.join(getcwd(), output_drawings_path)

    jpeg_ext = ".jpg"
    png_ext = ".png"
    webp_ext = ".webp"
    svg_ext = ".svg"

    image_conv_count = 0
    image_move_count = 0

    # Converting all raster assets to WEBP
    for root, _, files in walk(image_assets_folder):
        for file in files:
            asset_path = path.join(root, file)

            if file.endswith((jpeg_ext, png_ext)):
                asset_file_name, _ = path.splitext(file)
                converted_file_name = asset_file_name + webp_ext
                converted_output_path = path.join(output_image_folder, converted_file_name)
                
                asset_image = Image.open(asset_path).convert("RGB")
                asset_image.save(converted_output_path, "webp", quality=80)
                image_conv_count += 1
            elif file.endswith(webp_ext):
                migrate_output_path = path.join(output_image_folder, file)

                if path.exists(migrate_output_path):
                    unlink(migrate_output_path)

                shutil.copy2(asset_path, migrate_output_path)
                image_move_count += 1
                
            else:
                continue

    # TODO: Need to come up with ways to optimize SVG drawings
    if not path.exists(output_drawings_folder):
        makedirs(output_drawings_folder, exist_ok=True)

    for root, _, files in walk(drawings_assets_folder):
        for file in files:
            if file.endswith(svg_ext):
                drawing_path = path.join(root, file)
                target_drawing_path = path.join(output_drawings_folder, file)

                if path.exists(target_drawing_path):
                    unlink(target_drawing_path)
                
                shutil.copy(drawing_path, target_drawing_path)
                image_move_count += 1

    console.info(f"Asset processing: {image_conv_count} assets converted, {image_move_count} assets added")
