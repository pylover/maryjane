# -*- coding: utf-8 -*-

from .manifest import Manifest, ManifestObserver
import time
__author__ = 'vahid'
__version__ = '2.9'


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


def main(manifest_filename, enable_watcher=False, block=False, working_directory='.'):
    m = Manifest(manifest_filename, working_dir=working_directory)
    m.execute()
    if enable_watcher:
        watch(m, block=block)
    return m

