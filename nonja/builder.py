from os import path, walk, getcwd, makedirs, system
from jinja2 import Environment, FileSystemLoader

from nonja.style import bold, reset
import nonja.console as console
import nonja.filters as filters


def _run_package_manager():
    npm_lock_path = './package-lock.json'
    yarn_lock_path = './yarn.lock'

    if path.exists(npm_lock_path):
        system('npm run sass:build')
    elif path.exists(yarn_lock_path):
        system('yarn sass:build')
    elif not path.exists(npm_lock_path) and not path.exists(yarn_lock_path):
        console.error(f"Package lock files could not be found, ignoring.")


def build_project():
    _run_package_manager()
    
    content_folder_path = path.join(getcwd(), 'src/content')
    if not path.exists(content_folder_path):
        console.error(f"Content source path {bold}{content_folder_path}{reset} could not be found")
        exit(0)
    else:
        console.info(f"Processing content from folder {bold}{content_folder_path}{reset}")

    console.debug('Setting up Jinja environment.')
    env = Environment(
        loader=FileSystemLoader(content_folder_path),
        autoescape=True
    )

    env.filters={
        'date': filters.datetime_format
    }

    env.globals.update(
        path_for=filters.path_for,
        site=filters.site,
        dev=filters.dev
    )

    source_folder_path = 'src/content'
    build_target_path = 'build'
    
    for cwd, _, files in walk(content_folder_path):
        for file in files:
            if file.startswith('_'):
                continue

            # try:
            content_file_path = path.join(cwd.replace(content_folder_path, ''), file)
            if content_file_path.startswith('/'):
                content_file_path = content_file_path[1:]

            template = env.get_template(content_file_path)
            result = template.render()

            output_file_path = path.join(cwd, f"{file}").replace(source_folder_path, build_target_path)
            output_folder_path = path.dirname(output_file_path)
            
            if not path.exists(output_folder_path):
                console.debug(f"Created folder path {bold}{output_folder_path}{reset}")
                makedirs(output_folder_path, exist_ok=True)

            with open(output_file_path, 'wb') as output_file:
                console.debug(f"Writing output for {bold}{output_file_path}{reset}")
                output_file.write(result.encode())

            # except Exception as ex:
            #     console.error(f"Error encountered: {ex}")

    # Create robots.txt
    robots_file_content = '''
# www.robotstxt.org/

# Allow crawling for all content
User-agent: *
Disallow:

'''
    robots_file_path = './build/robots.txt'
    with open(robots_file_path, 'wb') as robots_file:
        robots_file.write(robots_file_content.encode())
    
    console.info(f"Wrote {bold}robots.txt{reset} for the site.")

