import re


"""
These methods sort a list of alphanumeric values in a human sortable way.  Default sort behaviour is lexicographic.
eg. [thing 9, thing 10, thing 11] as opposed to [thing 10, thing 11, thing 9]
"""
def tryint(s):
    try:
        return int(s)
    except:
        return s


def ALPHANUM_KEY(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]
