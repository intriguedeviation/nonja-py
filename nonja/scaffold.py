from os import makedirs, path, getcwd

from nonja.style import bold, reset
import nonja.console as console

def scaffold_project(*args):
    _create_source_folders()

    if args[0] == 'start' or args[0] == 'web':
        _create_npm_package('web')
    elif args[0] == 'book':
        _create_npm_package('book')
        _create_mimetype()

# ---

def _create_source_folders():
    project_paths = [
        path.join(getcwd(), 'build'),
        path.join(getcwd(), 'src/content'),
        path.join(getcwd(), 'src/data'),
        path.join(getcwd(), 'src/drawings'),
        path.join(getcwd(), 'src/images'),
        path.join(getcwd(), 'src/styles')
    ]

    console.info(f"Scaffolding project structure in {bold}{getcwd()}{reset}")
    for project_path in project_paths:
        if not path.exists(project_path):
            console.info(f"Creating path {bold}{project_path}{reset}")
            makedirs(project_path)
        else:
            console.info(f"Path {bold}{project_path}{reset} exists, skipping.")


def _create_npm_package(project_type):
    # Create package manifest for use with NPM / Yarn
    package_content = {
        'name': 'untitled-site' if project_type == 'web' else 'untitled-book',
        'version': '1.0.0',
        'description': 'Package file for Node-based tools and resources',
        'private': True,
        'license': 'UNLICENSED',
        'nonjaProject': {
            'title': 'Untitled Site' if project_type == 'web' else 'Untitled Book',
            'author': 'Untitled Site Team' if project_type == 'web' else 'Untitled Book Team',
            'description': 'A description of the untitled pages.',
            'domain': 'http://tempuri.org',
            'projectType': project_type
        },
        'dependencies': {
            'sass': 'latest'
        },
        'scripts': {
            'sass:build': 'sass ./src/styles:./build/assets/styles -s compressed --no-source-map',
            'sass:watch': 'sass ./src/styles:./build/assets/styles -s compressed -w --no-source-map',
        }
    }

    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'w') as package_file:
        import json
        json.dump(package_content, package_file, indent=2)

    console.info(f"Wrote package manifest {bold}{package_file_path}{reset}")


def _create_mimetype():
    mimetype_file_path = path.join(getcwd(), 'build/mimetype')
    with open(mimetype_file_path, 'wb') as mimetype_file:
        mimetype_file.write('application/epub+zip'.encode('ascii'))
    
    console.info(f"Wrote epub mimetype file {bold}{mimetype_file}{reset}")
