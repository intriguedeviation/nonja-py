from nonja.style import red, bold, reset

version = '0.1.0'

def print_usage():
    print("Starting:")
    print("  TODO")
    print('')
    print(f"  {bold}build{reset}       Combines the content and template files for output.")
    print(f"  {bold}serve{reset}       Serves the contents of the build folder.")
    print('')
    print(f"  {bold}publish{reset}     {red}Not implemented{reset}")
    print(f"  {bold}nuke{reset}        Deletes all content and configuration folders {red}(USE WITH CAUTION){reset}")

