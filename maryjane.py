"""

           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                   Version 2, December 2004

Copyright (C) 2016 Vahid Mardani

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 0. You just DO WHAT THE FUCK YOU WANT TO.


"""
import re
from os.path import abspath, dirname
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    # noinspection PyPackageRequirements
    import sass as libsass
except ImportError:
    libsass = None


__version__ = '4.2.0b4'


SPACE_PATTERN = '(?P<spaces>\s*)'
VALUE_PATTERN = '\s?(?P<value>.*)'
KEY_VALUE_PATTERN = re.compile('^{SPACE_PATTERN}(?P<key>[a-zA-Z0-9_]+):{VALUE_PATTERN}'.format(**locals()))
LIST_ITEM_PATTERN = re.compile('^{SPACE_PATTERN}-{VALUE_PATTERN}'.format(**locals()))
COMMENT_PATTERN = re.compile('^{SPACE_PATTERN}#{VALUE_PATTERN}'.format(**locals()))
INTEGER_PATTERN = re.compile('^\d+$')
FLOAT_PATTERN = re.compile('^\d*\.\d+$')


class MaryjaneSyntaxError(SyntaxError):
    def __init__(self, line_number, line, msg='Cannot parse here'):
        self.line_number = line_number
        self.line = line
        super().__init__('%s\n%d: %s' % (msg, line_number, line))


class DictNode(dict):

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(item)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            dict.__setattr__(self, key, value)
        self[key] = value


class WatcherEventHandler(FileSystemEventHandler):
    def __init__(self, project):
        self.project = project
        super(FileSystemEventHandler, self).__init__()

    def on_any_event(self, event):
        self.project.reload()


class MultiLineValueDetected(Exception):
    pass


class Project(object):
    watcher = None
    watch_handler = None

    def __init__(self, filename, dict_type=DictNode, list_type=list, opener=open, watcher=None, watcher_type=Observer):
        self.filename = filename
        self.dict_type = dict_type
        self.list_type = list_type
        self.opener = opener
        self.line_cursor = 0
        self.indent_size = 0
        self.current_key = None
        self.stack = [dict_type()]
        self.multiline_capture = None

        if watcher:
            self.watcher = watcher
        elif watcher_type:
            self.watcher = watcher_type()

        if self.watcher:
            self.watch_handler = WatcherEventHandler(self)

        globals().update(here=abspath(dirname(filename)))
        with opener(filename) as f:
            for l in f:
                self.line_cursor += 1
                if not l.strip() or COMMENT_PATTERN.match(l):
                    continue
                self.parse_line(l)

    def reload(self):
        if self.watcher:
            self.watcher.unschedule_all()

        print("Reloading")
        self.__init__(
            self.filename,
            dict_type=self.dict_type,
            list_type=self.list_type,
            opener=self.opener,
            watcher_type=None,
            watcher=self.watcher
        )

    def watch(self, path, recursive=False):
        if self.watcher is None:
            return

        print('Watching for %s' % path)
        self.watcher.schedule(self.watch_handler, path, recursive=recursive)

    def unwatch(self, path):
        if self.watcher is None:
            return

        # noinspection PyProtectedMember
        for w in self.watcher._watches:
            if w.path == path:
                print('Un-watching for %s' % path)
                self.watcher.unschedule(w)

    @property
    def current(self):
        return self.stack[-1]

    @property
    def level(self):
        return len(self.stack) - 1

    @property
    def root(self):
        return self.stack[0]

    def locals(self):
        for node in self.stack[::-1]:
            if isinstance(node, dict):
                return node

    def parse_value(self, v):
        if v is None:
            return None

        if self.multiline_capture is None and v.startswith('$$'):
            # Start Capture
            self.multiline_capture = v[2:] + '\n'
            raise MultiLineValueDetected()
        elif self.multiline_capture is not None and v.endswith('$$\n'):
            # End Capture
            v = self.multiline_capture + v[:-3]
            self.multiline_capture = None
        elif self.multiline_capture is not None:
            self.multiline_capture += v
            raise MultiLineValueDetected()
        else:
            v = v.strip()
            if not v:
                return None

        if INTEGER_PATTERN.match(v):
            return int(v)
        elif FLOAT_PATTERN.match(v):
            return float(v)
        else:
            return eval('f"""%s"""' % v, globals(), self.locals())

    def sub_parser(self, filename):

        parser = self.__class__(
            filename,
            dict_type=self.dict_type,
            list_type=self.list_type,
            opener=self.opener,
            watcher=self.watcher,
        )
        return parser

    def parse_line(self, line):
        key = None
        try:
            if self.multiline_capture is not None:
                line_data = self.indent_size * self.level, self.current_key, \
                            self.parse_value(line[(self.level + 1) * self.indent_size:])
            else:
                for pattern in [KEY_VALUE_PATTERN, LIST_ITEM_PATTERN]:
                    match = pattern.match(line)
                    if match:
                        line_data = match.groups()
                        break
                else:
                    raise MaryjaneSyntaxError(self.line_cursor, line, 'Cannot parse the line')

                spaces = len(line_data[0])
                if spaces:
                    if not self.indent_size:
                        self.indent_size = spaces
                    level = spaces // self.indent_size
                else:
                    level = 0

                if self.level < level:
                    # forward
                    parent_key = self.current_key
                    if self.current[parent_key] is None:
                        self.current[parent_key] = (self.list_type if len(line_data) == 2 else self.dict_type)()
                    self.stack.append(self.current[parent_key])
                elif self.level > level:
                    # backward
                    self.stack.pop()

            key = line_data[1] if len(line_data) > 2 else self.current_key

            if key.isupper():
                value = self.parse_value(line_data[len(line_data) - 1])
                if not value:
                    self.current[key] = None
                elif key == 'INCLUDE':
                    self.current.update(self.sub_parser(value).root)
                elif key == 'SHELL':
                    self.shell(value)
                elif key == 'ECHO':
                    print(value)
                elif key == 'PY':
                    exec(value, globals(), self.locals())
                elif key == 'WATCH':
                    self.watch(value)
                elif key == 'WATCH_ALL':
                    self.watch(value, recursive=True)
                elif key == 'NO_WATCH':
                    self.unwatch(value)
                elif key == 'SASS':
                    self.compile_sass(value)
                else:
                    raise MaryjaneSyntaxError(self.line_cursor, line, 'Invalid directive: %s' % key)

            elif isinstance(self.current, list):
                self.current.append(self.parse_value(line_data[1]))
            else:
                self.current[key] = self.parse_value(line_data[2])

            if not self.level:
                globals().update(self.current)

            self.current_key = key
        except MultiLineValueDetected:
            if key:
                self.current_key = key
            return



    @classmethod
    def shell(cls, cmd):
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            pass

    def wait_for_changes(self):
        self.watcher.start()
        self.watcher.join()

    @classmethod
    def compile_sass(cls, params):
        if libsass is None:
            raise ImportError(
                'In order, to use `SASS` tags, please install the `libsass` using: `pip install libsass`',
                name='libsass',
            )
        src, dst = params.split('>') if '>' in params else params.split(' ')
        src, dst = src.strip(), dst.strip()
        with open(dst, 'w') as f:
            f.write(libsass.compile(filename=src))


def quickstart(filename, watch=False):
    p = Project(filename, watcher_type=Observer if watch else None)
    if watch:
        return p.wait_for_changes()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='File watcher and task manager')
    parser.add_argument('manifest', nargs='?', default='maryjane.yaml', help='Manifest file, default: "maryjane.yaml"')
    parser.add_argument('-w', '--watch', dest='watch', action='store_true',
                        help='Watch for modifications, and execute tasks if needed.')
    parser.add_argument('-V', '--version', dest='version', action='store_true', help='Show version.')

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    try:
        return quickstart(args.manifest, args.watch)
    except FileNotFoundError:
        print(
            "No such file: 'maryjane.yaml', You must have a `maryjane.yaml` in the current directory or specify a "
            "manifest filename.", file=sys.stderr)
        parser.print_help()
    except KeyboardInterrupt:
        print('CTRL+C detected.')
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
