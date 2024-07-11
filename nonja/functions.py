from os import path, getcwd
from json import load
from markdown import markdown


def get_package_part():
    package_file_path = path.join(getcwd(), 'package.json')
    with open(package_file_path, 'r') as package_file:
        package_data = load(package_file)

    return package_data.get('nonjaProject', None)


def path_for(value: str) -> str:
    package_part = get_package_part()
    project_type = package_part.get('projectType', 'web')

    if project_type == 'web':
        output_url = '/'
        if value.endswith('index'):
            value = value[:-len('index')]
        
        output_url += value
        if not output_url.endswith('/'):
            output_url += '.html'

        return output_url
    elif project_type == 'book':
        output_url = value + '.xhtml'
        return output_url
    else:
        pass

    output_url = '/' if package_part.get('projectType', 'web') == 'web' else ''
    if value.endswith('index'):
        value = value[:-len('index')]
    
    output_url += value
    if not output_url.endswith('/'):
        output_url += ".html" if package_part.get('projectType', 'web') == 'web' else '.xhtml'

    return output_url


def import_json(value: str):
    data_file_path = path.join('src/data', f"{value}.json")
    if path.exists(data_file_path):
        with open(data_file_path, 'rb') as data_file:
            data_content = load(data_file)
            return data_content

    return []


def import_markdown(value: str):
    md_file_path = path.join('src/markdown', f"{value}.md")
    if path.exists(md_file_path):
        with open(md_file_path, 'rb') as md_file:
            md_content = md_file.read().decode()
            return markdown(md_content, extensions=['extra'])
        
    return ''


def _site_title():
    project_part = get_package_part()
    if project_part is None:
        return ''
    
    return project_part.get('title', '')


def _site_description():
    project_part = get_package_part()
    if project_part is None:
        return ''
    
    return project_part.get('description', '')


def _site_url():
    project_part = get_package_part()
    if project_part is None:
        return ''
    
    return project_part.get('domain', '')


def _site_author():
    project_part = get_package_part()
    if project_part is None:
        return ''
    
    return project_part.get('author', '')


site = {
    'title': _site_title,
    'description': _site_description,
    'url': _site_url,
    'author': _site_author
}
