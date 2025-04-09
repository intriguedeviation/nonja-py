"""Migration module for updating from prior versions of the tool."""

from os import path, getcwd, walk, unlink

from nonja.style import bold, reset
import nonja.console as console


def migrate_content():
    content_path = "./src/content"
    content_folder = path.join(getcwd(), content_path)
    source_extension = ".html"
    target_extension = ".j2"

    console.info(f"Beginning migration of {bold}HTML{reset} to {bold}J2{reset}.")

    for root, _, files in walk(content_folder):
        for file in files:
            if not file.endswith(source_extension):
                continue
        
            console.debug(f"\tFound file {bold}{file}{reset}.")

            source_file_path = path.join(root, file)
            target_file_name = file.replace(source_extension, target_extension)
            output_file_path = path.join(root, target_file_name)

            if path.exists(output_file_path):
                console.info(f"\tTarget {bold}{output_file_path}{reset} exists, skipping.")
                continue
            else:
                with open(source_file_path, 'rb') as source_file:
                    source_file_content = source_file.read()
                    with open(output_file_path, 'wb') as target_file:
                        target_file.write(source_file_content)

                console.info(f"\tMigrated {bold}{file}{reset} to J2.")
                unlink(source_file_path)
