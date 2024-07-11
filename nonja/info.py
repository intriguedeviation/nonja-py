from nonja.style import bold, reset

version = '0.1.5-dev'


def print_usage():
    print(f"  {bold}init{reset}        Generates the necessary structure and basic components for a project.")
    print(f"  {bold}generate{reset}    Also {bold}g{reset}; generates an asset for the project.")
        
    print('')
    print(f"  {bold}build{reset}       Also {bold}b{reset}; combines the content and template files for output.")
    print(f"  {bold}serve{reset}       Serves the contents of the build folder.")

