# -*- coding: utf-8 -*-
__author__ = 'vahid'
import argparse
import os
import sys
from maryjane import main

parser = argparse.ArgumentParser(description='File watcher and task manager')
parser.add_argument('manifest', nargs='?', default='maryjane.yaml', help='Manifest file, default: "maryjane.yaml"')
parser.add_argument('-d', '--working-directory', metavar='WORKING_DIR', default='.', dest='working_dir', help='Working directory, default: current directory: %s' % os.path.abspath(os.curdir))
parser.add_argument('-w','--watch', dest='watch', action='store_true', help='Watch for modifications, and execute tasks if needed.')

def cli_main():
    args = parser.parse_args()
    main(args.manifest,
         enable_watcher=args.watch,
         block=args.watch,
         working_directory=args.working_dir)
    sys.exit(0)
