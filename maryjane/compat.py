import sys

if sys.version_info[0] < 3:
    # python 2
    # noinspection PyUnresolvedReferences
    basestring = basestring

else:
    # python 3
    basestring = str
