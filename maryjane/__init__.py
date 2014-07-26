# -*- coding: utf-8 -*-

from .manifest import Manifest
__author__ = 'vahid'


def main(manifest_filenames, enable_watch=False):

    if isinstance(manifest_filenames, basestring):
        manifest_filenames = manifest_filenames.split()

    m = Manifest()
    for manifest_filename in manifest_filenames:
        with open(manifest_filename) as manifest_file:
            m.load(manifest_file)
    m.execute()

    if enable_watch:
        m.watch()

