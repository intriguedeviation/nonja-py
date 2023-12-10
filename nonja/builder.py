from os import path, walk, getcwd, makedirs
from jinja2 import Environment, FileSystemLoader

from nonja.style import bold, reset
import nonja.console as console
import nonja.filters as filters

def build_project():
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

    source_folder_path = 'src/content'
    build_target_path = 'build'
    
    for cwd, _, files in walk(content_folder_path):
        for file in files:
            if file.startswith('_'):
                continue

            # try:
            content_file_path = path.join('about', file)
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


