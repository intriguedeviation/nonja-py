from sys import argv

from nonja.style import reset, blue
from nonja.info import version, print_usage
from nonja.server import run as run_server
from nonja.scaffold import scaffold_project
from nonja.builder import build_project, rebuild_project
from nonja.generator import generate_content


def main():
    print(f"{blue}Nonja SSG{reset} for Python v{version}")
    print('Docs available from https://nonja.intriguedeviation.com')
    print('')
    
    if len(argv) == 1:
        print_usage()
        exit(0)

    command = argv[1]
    if command == 'serve':
        run_server()
    elif command == 'start':
        print(f"Count of arguments for start command: {len(argv)}")
        args = argv[2:] if len(argv) >= 3 else argv[1:]
        scaffold_project(*args)
    elif command == 'build' or command == 'b':
        build_project()
    elif command == 'rebuild' or command == 'rb':
        rebuild_project()
    elif command == 'generate' or command == 'g':
        generate_content(*argv[2:])

