import json
import lxml.etree as et
from os import path, walk, getcwd, makedirs, system, removedirs, remove
from jinja2 import Environment, FileSystemLoader
from lxml.builder import E
from datetime import datetime

from nonja.style import bold, reset
import nonja.console as console
import nonja.filters as filters
import nonja.functions as functions


def _run_package_manager():
    # TODO: Feels like there might be a better manner of handling invoking the package manager.
    npm_lock_path = './package-lock.json'
    yarn_lock_path = './yarn.lock'

    if path.exists(npm_lock_path):
        system('npm run sass:build')
    elif path.exists(yarn_lock_path):
        system('yarn sass:build')
    elif not path.exists(npm_lock_path) and not path.exists(yarn_lock_path):
        console.error("Package lock files could not be found, ignoring.")


def rebuild_project():
    # Remove existing build folder
    # TODO: Need to use file removal methods from Python instead of this.
    build_folder_path = path.join('.', 'build')
    system(f"rm -rf {build_folder_path}")
    build_project()


def build_project():
    _run_package_manager()
    
    content_folder_path = path.join(getcwd(), 'src/content')
    if not path.exists(content_folder_path):
        console.error(f"Content source path {bold}{content_folder_path}{reset} could not be found")
        exit(0)
    else:
        console.info(f"Processing content from folder {bold}{content_folder_path}{reset}")

    console.info('Setting up Jinja environment.')
    env = Environment(
        loader=FileSystemLoader(content_folder_path),
        autoescape=True
    )

    env.filters={
        'date': filters.datetime_format
    }

    env.globals.update(
        path_for=functions.path_for,
        site=functions.site
    )

    source_folder_path = 'src/content'
    build_target_path = 'build'

    build_tally = 0

    for cwd, _, files in walk(content_folder_path):
        for file in files:
            if file.startswith('_') or not file.endswith('.html'):
                continue

            content_file_path = path.join(cwd.replace(content_folder_path, ''), file)
            if content_file_path.startswith('/'):
                content_file_path = content_file_path[1:]

            template = env.get_template(content_file_path)
            result = template.render()

            output_file_path = path.join(cwd, f"{file}").replace(source_folder_path, build_target_path)
            output_folder_path = path.dirname(output_file_path)
            
            if not path.exists(output_folder_path):
                makedirs(output_folder_path, exist_ok=True)

            with open(output_file_path, 'wb') as output_file:
                output_file.write(result.encode())
                build_tally += 1

    console.info(f"Wrote {bold}{build_tally}{reset} pages for the project.")
    _write_robots_file()
    _write_sitemap()


def _write_sitemap():
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'rb') as package_file:
        package_content = json.load(package_file)
    
    project_config = package_content.get('nonjaProject')
    project_base_url = project_config.get('domain')

    build_folder_path = path.join(getcwd(), 'build')
    sitemap_node_count = 0
    sitemap_content = E.sitemap(
        {
            'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
        }
    )
    for cwd, _, files in walk(build_folder_path):
        for filename in files:
            if not filename.endswith('.html'):
                continue

            file_path = path.join(cwd, filename).replace(path.join(getcwd(), 'build'), project_base_url).replace('index.html', '')
            sitemap_content.append(E.url(
                E.loc(file_path),
                E.lastmod(datetime.now().strftime('%Y-%m-%d'))
            ))
            sitemap_node_count += 1

    sitemap_file_path = path.join(getcwd(), 'build/sitemap.xml')
    with open(sitemap_file_path, 'wb') as sitemap_file:
        sitemap_file.write(et.tostring(sitemap_content, pretty_print=True))

    console.info(f"Wrote site map data file {bold}{sitemap_file_path}{reset} for {sitemap_node_count} url nodes")


def _write_robots_file():
    # Create robots.txt
    robots_file_content = '''# www.robotstxt.org/

# Allow crawling for all content
User-agent: *
Disallow:
'''
    robots_file_path = './build/robots.txt'
    with open(robots_file_path, 'wb') as robots_file:
        robots_file.write(robots_file_content.encode())
    
    console.info(f"Wrote {bold}robots.txt{reset} for the project.")