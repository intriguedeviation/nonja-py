from sys import argv

from nonja.style import reset, blue
from nonja.info import version, print_usage
from nonja.server import run as run_server
from nonja.scaffold import scaffold_project
from nonja.builder import build_project
from nonja.generator import generate_content


def main():
    print(f"{blue}Nonja SSG{reset} for Python v{version}")
    
    if len(argv) == 1:
        print_usage()
        exit(0)

    command = argv[1]
    if command == 'serve':
        run_server()
    elif command == 'start':
        scaffold_project()
    elif command == 'build' or command == 'b':
        build_project()
    elif command == 'generate' or command == 'g':
        generate_content(*argv[2:])

