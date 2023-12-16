from os import getcwd, path, makedirs
from datetime import datetime
from lxml.builder import E
import lxml.etree as et

import nonja.console as console
from nonja.style import bold, reset

def generate_content(*args):
    if len(args) == 0:
        console.warn(f"Received no arguments for generation, ignoring.")
        exit(0)
    
    generators = {
        'page': _generate_page,
        'template': _generate_template,
        'style': _generate_style,
        'drawing': _generate_drawing,
        'gitignore': _generate_gitignore,
        'docker-compose': _generate_docker_compose
    }

    generator_key = args[0]
    if generator_key in generators.keys():
        generator = generators[generator_key]
        generator(*args[1:])
    else:
        console.warn(f"Unknown generator requested with {bold}{generator_key}{reset}, ignoring")
        exit(0)


def _generate_page(filename, template_name='shared'):
    console.debug(f"Page generation requested for page {bold}{filename}{reset} with template {bold}{template_name}{reset}")

    page_content = '{%' + f" extends '_{template_name}.html' " + '%}' + _page_default

    page_path = path.join(getcwd(), f"src/content/{filename}.html")
    page_folder_path = path.dirname(page_path)
    if not path.exists(page_folder_path):
        makedirs(page_folder_path, exist_ok=True)
        console.debug(f"Created path for page source at {bold}{page_folder_path}{reset}")

    with open(page_path, 'wb') as page_file:
        page_file.write(page_content.encode())

    template_file_path = path.join(getcwd(), f"src/content/_{template_name}.html")
    if not path.exists(template_file_path):
        _generate_template(template_name)


def _generate_template(template_name):
    console.debug(f"Template generation requested for template {bold}{template_name}{reset}")

    template_file_path = path.join(getcwd(), f"src/content/_{template_name}.html")
    with open(template_file_path, 'wb') as template_file:
        template_file.write(_template_default.encode())
    

def _generate_style(style_name):
    scss_content = f"// File:      {style_name}.scss\n" + \
    f"// Generated: {datetime.now().strftime('%Y-%m-%d')}" + \
'''

// Add your style declarations for this file.
// Reference available from https://sass-lang.com
// and playground available at https://www.sassmeister.com/
'''
    
    scss_file_path = path.join(getcwd(), f"src/styles/{style_name}.scss")
    with open(scss_file_path, 'wb') as scss_file:
        scss_file.write(scss_content.encode())
    
    console.info(f"Created SCSS file at {bold}{scss_file_path}{reset}")


def _generate_drawing(*args):
    drawing_name = args[0]
    width = args[1] if len(args) >= 2 else '400'
    height = args[2] if len(args) >= 3 else '400'

    svg_content = E.svg(
        {
            'xmlns': 'http://www.w3.org/2000/svg',
            'version': '1.1',
            'width': width,
            'height': height,
            'viewBox': f"0 0 {width} {height}"
        },
        et.Comment(f" File:      {drawing_name}.svg "),
        et.Comment(f" Generated: {datetime.now().strftime('%Y-%m-%d')} "),
        E.title(f"untitled drawing {drawing_name}"),
        E.defs(
            E.style(
                et.CDATA('\n/* Add style definitions within this CDATA section */\n\n')
            )
        ),
        E.g({'id': 'layer-1'})
    )

    svg_file_path = path.join(getcwd(), f"src/drawings/{drawing_name}.svg")
    with open(svg_file_path, 'wb') as svg_file:
        svg_file.write(et.tostring(svg_content, pretty_print=True))

    console.info(f"Generated drawing resource at {bold}{svg_file_path}{reset}")


def _generate_gitignore():
    file_path = path.join(getcwd(), '.gitignore')
    with open(file_path, 'wb') as gitignore_file:
        gitignore_file.write(_gitignore_content.encode())
    
    console.info(f"Generated gitignore at {bold}{file_path}{reset}")


def _generate_docker_compose():
    compose_file_content = {
        'services': {
            'static_site': {
                'image': 'httpd:2.4-alpine',
                'volumes': ['./build:/usr/local/apache2/htdocs:ro'],
                'ports': ['5000:80']
            }
        }
    }

    compose_file_path = path.join(getcwd(), 'docker-compose.yml')
    import yaml
    with open(compose_file_path, 'wb') as compose_file:
        compose_file.write(yaml.dump(compose_file_content).encode())
    
    console.info(f"Generated Docker Compose at {bold}{compose_file_path}{reset}")


_template_default = '''<!DOCTYPE html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="initial-scale=1.0, width=device-width">
        <title>{% block title %}{% endblock %}</title>
        {% block head %}{% endblock %}
    </head>
    <body>
        <!--Add template-level content here.-->
        {% block content %}{% endblock %}
    </body>
</html>
'''

_page_default = '''

{% block title %}{% endblock %}

{% block head %}
    <!-- Additional link, meta, style, or other elements. -->
{% endblock %}

{% block content %}
    <!-- Content block -->
{% endblock %}
'''

_gitignore_content = '''# gitignore
# generated by nonja

# macos noise
.DS_Store

# ide noise
.vscode
.idea

# nonja noise
build
env
node_modules
'''