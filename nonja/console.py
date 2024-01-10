from nonja.style import red, green, cyan, yellow, reset

_info = 'INFO'
_debug = 'DEBUG'
_warning = 'WARNING'
_error = 'ERROR'


def info(message: str) -> None:
    print(f"{green}{_info}{reset}: {message}")


def debug(message: str) -> None:
    print(f"{cyan}{_debug}{reset}: {message}")


def warn(message: str) -> None:
    print(f"{yellow}{_warning}{reset}: {message}")


def error(message: str) -> None:
    print(f"{red}{_error}{reset}: {message}")
