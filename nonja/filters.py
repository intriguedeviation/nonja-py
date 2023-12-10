"""Module for filters used by Jinja"""

from os import path, getcwd
from datetime import datetime
from json import load

import nonja.console as console

def datetime_format(value: datetime | str, format='%Y-%m-%d'):
    if value == 'now':
        return datetime.now().strftime(format)
    
    return value.strftime(format)


