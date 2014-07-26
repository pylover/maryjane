# -*- coding: utf-8 -*-
import sys
from .manifest import Manifest
__author__ = 'vahid'


def main(*manifest_filenames):
    m = Manifest()
    for manifest_filename in manifest_filenames:
        with open(manifest_filename) as manifest_file:
            m.load(manifest_file)
    m.execute()

