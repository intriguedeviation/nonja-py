from nonja.style import red, bold, reset

version = '0.1.0'

def print_usage():
    print(f"  {bold}start{reset}       Generates the necessary stucture and basic components for a project.")
    print(f"  {bold}generate{reset}    Also {bold}g{reset}; generates an asset for the project.")
        
    print('')
    print(f"  {bold}build{reset}       Also {bold}b{reset}; combines the content and template files for output.")
    print(f"  {bold}serve{reset}       Serves the contents of the build folder.")
    print('')
    print(f"  {bold}publish{reset}     {red}Not implemented{reset}")
    print(f"  {bold}nuke{reset}        Deletes all content and configuration folders {red}(USE WITH CAUTION){reset}")

