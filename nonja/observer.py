import os
from os import path
import time

from nonja.builder import build_project
import nonja.console as console


def watch_project():
    source_path = path.join(os.getcwd(), 'src/content')
    console.info(f"Watching for changes on {source_path}")
    _watch_files(source_path, _on_file_change)


def _watch_files(folder_path, callback):
    file_modification_times = _scan_path(folder_path)

    try:
        while True:
            for root, _, files in os.walk(folder_path):
                for filename in files:
                    file_path = path.join(root, filename)
                    current_mod_time = path.getmtime(file_path)
                    
                    last_mod_time = file_modification_times.get(file_path)

                    if current_mod_time > last_mod_time:
                        file_modification_times[file_path] = current_mod_time
                        callback(file_path)

            time.sleep(1)
    except KeyboardInterrupt:
        console.info("Shutting down watcher.")


def _scan_path(folder_path):
    scan_result = {}
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = path.join(root, filename)
            mod_time = path.getmtime(file_path)

            scan_result[file_path] = mod_time
    
    return scan_result


def _on_file_change(file_path):
    console.debug(f"Changed file: {file_path}")
    build_project()

