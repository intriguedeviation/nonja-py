from os import makedirs, path, getcwd

from nonja.style import bold, reset
import nonja.console as console

def scaffold_project():
    _create_source_folders()
    _create_npm_package()

    content_readme_path = path.join(getcwd(), 'src/README.md')
    if not path.exists(content_readme_path):
        with open(content_readme_path, 'w') as content_readme:
            content_readme.write("\n".join([
                '# Source files',
                '',
                f"Path: `{path.join(getcwd(), 'src')}`",
                '',
                'This is the source folder for your project. Each subfolder serves a particular purpose:',
                '',
                '* `content`: Contains the content pages for your site.',
                '* `data`: Contains data segments that can be imported into pages.',
                '* `drawings`: Contains any SVG assets you create for your site.',
                '* `images`: Contains image assets for your site.',
                '* `styles`: Contains SCSS assets that will be transformed to CSS.'
            ]))


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


def _create_npm_package():
    # Create package manifest for use with NPM / Yarn
    package_content = {
        'name': 'untitled-site',
        'version': '1.0.0',
        'description': 'Package file for Node-based tools and resources',
        'private': True,
        'license': 'UNLICENSED',
        'nonjaProject': {
            'title': 'Untitled Site',
            'author': 'Untitled Site Team',
            'description': 'A description of the untitled site',
            'domain': 'http://tempuri.org'
        },
        'dependencies': {
            'sass': 'latest'
        },
        'scripts': {
            'sass:build': 'sass ./src/styles:./build/assets/styles -s compressed',
            'sass:watch': 'sass ./src/styles:./build/assets/styles -s compressed -w',
        }
    }

    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'w') as package_file:
        import json
        json.dump(package_content, package_file, indent=2)

    console.info(f"Wrote package manifest {bold}{package_file_path}{reset}")