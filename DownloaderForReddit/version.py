__version__ = 'v3.0.1-beta'


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
