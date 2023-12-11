"""Module for filters used by Jinja"""

from os import path, getcwd
from datetime import datetime
from json import load

import nonja.console as console

def datetime_format(value: datetime | str, format='%Y-%m-%d'):
    if value == 'now':
        return datetime.now().strftime(format)
    
    return value.strftime(format)


def path_for(value: str) -> str:
    output_url = '/'
    if value.endswith('index'):
        value = value[:-len('index')]
    
    output_url += value
    if not output_url.endswith('/'):
        output_url += ".html"

    return output_url

# ---

def _site_title():
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'r') as package_file:
        package_data = load(package_file)

    project_part = package_data.get('ninjaProject', None)
    if project_part is None:
        return ''
    
    return project_part.get('title', '')


def _site_description():
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'r') as package_file:
        package_data = load(package_file)

    project_part = package_data.get('ninjaProject', None)
    if project_part is None:
        return ''
    
    return project_part.get('description', '')


def _site_url():
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'r') as package_file:
        package_data = load(package_file)

    project_part = package_data.get('ninjaProject', None)
    if project_part is None:
        return ''
    
    return project_part.get('domain', '')


def _site_author():
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'r') as package_file:
        package_data = load(package_file)

    project_part = package_data.get('ninjaProject', None)
    if project_part is None:
        return ''
    
    return project_part.get('author', '')

site = {
    'title': _site_title,
    'description': _site_description,
    'url': _site_url,
    'author': _site_author
}

# --

def _generate_cache_control():
    return '<meta http-equiv="Content-Type" content="no-cache">'

dev = {
    'cache': _generate_cache_control
}