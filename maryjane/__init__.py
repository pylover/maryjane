from .core import Project
from watchdog.observers import Observer
import argparse

__version__ = '4.0.0a3'

parser = argparse.ArgumentParser(description='File watcher and task manager')
parser.add_argument('manifest', nargs='?', default='maryjane.yaml', help='Manifest file, default: "maryjane.yaml"')
parser.add_argument('-w', '--watch', dest='watch', action='store_true',
                    help='Watch for modifications, and execute tasks if needed.')
parser.add_argument('-V', '--version', dest='version', action='store_true', help='Show version.')


def main():
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    p = Project(args.manifest, watcher_type=Observer if args.watch else None)
    if args.watch:
        try:
            return p.wait_for_changes()
        except KeyboardInterrupt:
            print('CTRL+C detected.')
            return 1
