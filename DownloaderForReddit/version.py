__version__ = 'v3.16.0'


def get_major_version():
    m = get_version_parts(__version__)[0]
    return int(m)


def get_minor_version():
    m = get_version_parts(__version__)[1]
    return int(m)


def get_patch_version():
    p = get_version_parts(__version__)[2]
    return int(p)


def get_version_parts(version_string):
    v = version_string.lower().replace('v', '')
    return v.split('.')


def is_updated(tested_for: str, tested_against: str) -> bool:
    tested_against = compile_version(tested_against)
    tested_for = compile_version(tested_for)
    return tested_for > tested_against


def compile_version(ver: str) -> int:
    return int(''.join(x for x in ver if x.isdigit()))


def update_type(ver: str) -> int:
    major, minor, patch = get_version_parts(ver)
    c_major, c_minor, c_patch = get_version_parts(__version__)
    if is_updated(major, c_major):
        return 3
    if is_updated(minor, c_minor):
        return 2
    if is_updated(patch, c_patch):
        return 1
    return 0
