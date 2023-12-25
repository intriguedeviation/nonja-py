"""Module for filters used by Jinja"""

from datetime import datetime
from markupsafe import Markup


def datetime_format(value: datetime | str, format='%Y-%m-%d'):
    if value == 'now':
        return datetime.now().strftime(format)
    
    return value.strftime(format)


def encode(value: str) -> Markup:
    return Markup(value.encode('ascii', 'xmlcharrefreplace').decode())

