# -*- coding: utf-8 -*-

from .manifest import Manifest
__author__ = 'vahid'
__version__ = '2.2'

def main(manifest_filename, watch=False, block=False, working_directory='.'):

    m = Manifest(manifest_filename,
                 working_dir=working_directory)
    m.execute()

    if watch:
        m.watch(block=block)

