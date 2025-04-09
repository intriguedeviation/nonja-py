from argparse import ArgumentParser

from nonja.info import version
from nonja.server import run as run_server
from nonja.scaffold import scaffold_project
from nonja.builder import build_project
from nonja.generator import generate_content
from nonja.observer import watch_project
from nonja.migrator import migrate_content

def main():
    parser = ArgumentParser(description=f"Nonja SSG for Python v{version}")
    subparsers = parser.add_subparsers(dest="command", required=False)
    
    subparsers.add_parser("init-web", help="Initializes a new web project", aliases=["iw", "i"])
    subparsers.add_parser("init-epub", help="Initializes a new EPUB project", aliases=["ib"])
    subparsers.add_parser("serve-proj", help="Launches a local web server for the build content.", aliases=["s"])

    build_parser = subparsers.add_parser("build", help="Builds the current project content.", aliases=["b"])
    build_parser.add_argument("--include-assets", action="store_true")
    
    gen_parser = subparsers.add_parser("generate", help="Generates a scaffold for project content.", aliases=["g"])
    gen_parser.add_argument("type", action="store", choices=["page", "template", "style", "drawing", "data", "markdown", "project-file"])
    gen_parser.add_argument("name", action="store")
    gen_parser.add_argument("options", action="store", nargs="?", default="")
    
    subparsers.add_parser("watch", help="Starts a watcher process to rebuild the project content when files change.", aliases=["w"])
    
    subparsers.add_parser("upgrade", help="Upgrades a prior project format to this version of Nonja.")

    try:
        args = parser.parse_args()

        if args.command == "init-web" or args.command == "iw" or args.command == "i":
            scaffold_project(type="web")
        elif args.command == "init-epub" or args.command == "ib":
            scaffold_project(type="book")
        elif args.command == "serve-proj" or args.command == "s":
            run_server()
        elif args.command == "build" or args.command == "b":
            build_project(**{
                "include-assets": args.include_assets
            })
        elif args.command == "generate" or args.command == "g":
            generate_content(*[
                args.type,
                args.name,
                args.options
            ])
        elif args.command == "watch" or args.command == "w":
            watch_project()
        elif args.command == "upgrade":
            migrate_content()
    except Exception as e:
        print(e)
