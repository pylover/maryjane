
from .core import Project
import argparse
import sys


__version__ = '3.0.0'


parser = argparse.ArgumentParser(description='File watcher and task manager')
parser.add_argument('manifest', nargs='?', default='maryjane.yaml', help='Manifest file, default: "maryjane.yaml"')


def main():
    args = parser.parse_args()
    Project(args.manifest)
    sys.exit(0)
