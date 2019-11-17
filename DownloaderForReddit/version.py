# __version__ = 'v2.3.2'
__version__ = 'v3.0.0'


def get_major_version():
    m = get_version_parts(__version__)[0]
    return int(m)


def get_minor_version():
    m = get_version_parts(__version__)[1]
    return int(m)


def get_patch_version():
    p = get_version_parts(__version__)[3]
    return int(p)


def get_version_parts(version_string):
    v = version_string.replace('v', '')
    return v.split('.')
