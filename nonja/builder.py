import json
import lxml.etree as et
from os import path, walk, getcwd, makedirs, system
from jinja2 import Environment, FileSystemLoader
from lxml.builder import E, ElementMaker
from datetime import datetime
from json import load
from uuid import uuid4

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
    project_config = _get_project_config()
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
        'date': filters.datetime_format,
        'encode': filters.encode,
        # 'yahv': filters.yahv
    }

    env.globals.update(
        path_for=functions.path_for,
        site=functions.site,
        data=functions.import_json
    )

    source_folder_path = 'src/content'
    build_target_path = 'build' if project_config.get('projectType', 'web') == 'web' else 'build/content'

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
            
            if project_config.get('projectType', 'web') == 'book':
                output_file_path = output_file_path.replace('.html', '.xhtml')

            with open(output_file_path, 'wb') as output_file:
                output_file.write(result.encode())
                build_tally += 1

    console.info(f"Wrote {bold}{build_tally}{reset} pages for the project.")

    if project_config.get('projectType', 'web') == 'web':
        _write_robots_file()
        _write_sitemap()
    else:
        _write_container()
        _write_opf_package()
        _write_mimetype()


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


def _get_project_config():
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'rb') as package_file:
        package_content = load(package_file)
    
    return package_content.get('nonjaProject', None)


def _write_container():
    container_content = E.container({
        'xmlns': 'urn:oasis:names:tc:opendocument:xmlns:container',
        'version': '1.0'
        },
        E.rootfiles(
            E.rootfile({ 'full-path': 'content/source.opf', 'media-type': 'application/oebps-package+xml'})
        )
    )

    container_file_path = path.join(getcwd(), 'build/META-INF/container.xml')
    if not path.exists(path.dirname(container_file_path)):
        makedirs(path.dirname(container_file_path), exist_ok=True)
    
    with open(container_file_path, 'wb') as container_file:
        container_file.write(et.tostring(container_content))
    
    console.info(f"Wrote container file for OEBPS pub format {bold}{container_file_path}{reset}.")


def _write_opf_package():
    config = _get_project_config()
    unique_id = str(uuid4())
    build_path = path.join(getcwd(), 'build/content')

    items = []
    spines = []

    for cwd, _, files in walk(build_path):
        files.sort()
        for filename in files:
            if filename.endswith('.opf'):
                continue

            item_identifier = f"content-{uuid4()}"
            item_data = {
                'id': item_identifier,
                'href': path.join(cwd, filename).replace(f"{build_path}/", '')
            }

            if filename.endswith('.xhtml'):
                item_data['media-type'] = 'application/xhtml+xml'
                if filename == 'nav.xhtml':
                    item_data['properties'] = 'nav'
                    spines.insert(0, E.itemref({'idref': item_identifier}))
                else:                
                    spines.append(E.itemref({'idref': item_identifier}))
            elif filename.endswith('.css'):
                item_data['media-type'] = 'text/css'
            elif filename.endswith('.svg'):
                item_data['media-type'] = 'image/svg+xml'
            elif filename.endswith('.webp'):
                item_data['media-type'] = 'image/webp'
            elif filename.endswith('.png'):
                item_data['media-type'] = 'image/png'
            elif filename.endswith('.jpg'):
                item_data['media-type'] = 'image/jpeg'
            
            if filename == 'nav.xhtml':
                items.insert(0, E.item(item_data))
            else:
                items.append(E.item(item_data))

    
    em = ElementMaker(namespace='http://www.idpf.org/2007/opf', nsmap={None: 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/'})
    dc = ElementMaker(namespace='http://purl.org/dc/elements/1.1/', nsmap={'dc': 'http://purl.org/dc/elements/1.1/'})
    
    book_identifier = 'book-' + unique_id
    package_content = em.package(
        {
            'version': '3.0',
            'dir': 'ltr',
            'unique-identifier': book_identifier
        },
        em.metadata(
            dc.identifier(
                {'id': book_identifier},
                f"urn:uuid:{unique_id}"
            ),
            dc.title(
                config.get('title')
            ),
            dc.language(
                'en-US'
            ),
            dc.creator(
                config.get('author')
            ),
            em.meta(
                {'property': 'dcterms:modified'},
                datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        ),
        em.manifest(*items),
        em.spine(*spines)
    )

    package_file_path = path.join(getcwd(), 'build/content/source.opf')
    with open(package_file_path, 'wb') as package_file:
        package_file.write(et.tostring(package_content, pretty_print=True))
    
    console.info(f"Wrote OPF package file {bold}{package_file_path}{reset}")


def _write_mimetype():
    content_file_path = path.join(getcwd(), 'build/mimetype')
    with open(content_file_path, 'wb') as content_file:
        content = 'application/epub+zip'
        content_file.write(content.encode('ascii'))
    
    console.info(f"Wrote media type identification {bold}{content_file_path}{reset}")
