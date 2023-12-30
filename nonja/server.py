from http.server import HTTPServer, SimpleHTTPRequestHandler
from os import path, getcwd
from json import load

from nonja.style import red, green, bold, reset

class BuildFolderHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        content_path = path.join(getcwd(), 'build')
        super().__init__(*args, directory=content_path, **kwargs)


def run(server_class=HTTPServer, handler_class=BuildFolderHandler):
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'rb') as package_file:
        package = load(package_file)
    
    project_type = package.get('projectType', 'web')
    content_path_part = 'build' if project_type == 'web' else 'build/content'

    content_path = path.join(getcwd(), content_path_part)
    if not path.exists(content_path):
        print(f"{red}ERROR{reset}: Content folder, {bold}{content_path}{reset} could not be found, aborting.")
        exit(0)

    try:
        server_address = ('127.0.0.1', 5000)
        print(f"{green}INFO{reset}: Serving content from {bold}{content_path}{reset} through {bold}http://{server_address[0]}:{server_address[1]}{reset}")
        httpd = server_class(server_address, handler_class)
        handler_class.directory = './build'
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"{green}INFO{reset}: Development server shutting down")
