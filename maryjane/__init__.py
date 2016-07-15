# -*- coding: utf-8 -*-

from .manifest import Manifest, ManifestObserver
import time
import os
import traceback
__author__ = 'vahid'
__version__ = '3.0.0'


def watch(manifest_to_watch, block=False):
    observer = ManifestObserver(manifest_to_watch)
    observer.start()
    if block:
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                observer.join()
                break


def main(manifest_filename, enable_watcher=False, block=False, working_directory='.', bootstrap=True):
    m = Manifest(manifest_filename, working_dir=os.path.abspath(working_directory))
    if bootstrap:
        try:
            m.execute()
        except:
            traceback.print_stack()
            traceback.print_exc()

    if enable_watcher:
        watch(m, block=block)
    return m

