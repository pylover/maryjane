
from .core import Project
from watchdog.observers import Observer
import argparse
import sys


__version__ = '4.0.0'


parser = argparse.ArgumentParser(description='File watcher and task manager')
parser.add_argument('manifest', nargs='?', default='maryjane.yaml', help='Manifest file, default: "maryjane.yaml"')
parser.add_argument('-w','--watch', dest='watch', action='store_true', help='Watch for modifications, and execute tasks if needed.')


def main():
    args = parser.parse_args()
    p = Project(args.manifest, watcher_type=Observer if args.watch else None)
    if args.watch:
        try:
            sys.exit(p.wait_for_changes())
        except KeyboardInterrupt:
            print('CTRL+C detected.')
            sys.exit(1)
