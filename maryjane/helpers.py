# -*- coding: utf-8 -*-
import os
import glob
from maryjane.compat import basestring
__author__ = 'vahid'


def split_paths(p):
    if isinstance(p, basestring):
        # noinspection PyUnresolvedReferences
        res = p.split(',')
    else:
        res = p
    return [os.path.abspath(i.strip()) for i in res]


def distinct(l):
    if not l or not len(l):
        return []
    return list(set(l))


def get_source_files(sources, extensions='.sass,.scss'):
    source_files = []
    for s in sources:
        p = os.path.abspath(s)
        if os.path.isfile(p):
            source_files.append(p)
        elif os.path.isdir(p):
            for extension in extensions.split(','):
                for _f in glob.iglob(os.path.join(p,'*%s' % extension)):
                    source_files.append(os.path.abspath(_f))
    return sorted(distinct(source_files))


def get_source_dirs(sources):
    source_dirs = []
    for s in split_paths(sources):
        if os.path.isdir(s):
            source_dirs.append(s)
        else:
            p = os.path.abspath(os.path.dirname(s))
            if os.path.isdir(p):
                source_dirs.append(p)

    return sorted(distinct(source_dirs))


def has_file_overlap(paths1, paths2):
    for p1 in split_paths(paths1):
        if not os.path.isfile(p1):
            continue
        for p2 in split_paths(paths2):
            if not os.path.isfile(p2):
                continue
            if os.path.samefile(p1, p2):
                return True
    return False

def get_filename(filepath):
    return os.path.split(filepath)[1]
