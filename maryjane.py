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
from os.path import abspath, dirname, isdir
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    # noinspection PyPackageRequirements
    import sass as libsass
except ImportError:  # pragma: no cover
    libsass = None


__version__ = '4.3.6b4'


SPACE_PATTERN = '(?P<spaces>\s*)'
VALUE_PATTERN = '\s?(?P<value>.*)'
KEY_VALUE_PATTERN = re.compile('^{SPACE_PATTERN}(?P<key>[a-zA-Z0-9_-]+):{VALUE_PATTERN}'.format(**locals()))
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
    def __init__(self, project, filter_key=None):
        self.project = project
        self.filter_key = filter_key
        super(FileSystemEventHandler, self).__init__()

    def on_any_event(self, event):
        src_path = event.src_path
        src_dir = dirname(src_path)

        excludes = self.project.watch_excludes.get(self.filter_key)
        if excludes and (src_path in excludes or src_dir in excludes):
            return

        includes = self.project.watch_includes.get(self.filter_key)
        for include in includes:
            include_dir = abspath(dirname(include))
            if src_dir == include_dir and src_path not in include:
                return

        self.project.reload(filter_key=self.filter_key)


class MultiLineValueDetected(Exception):
    pass


class Project(object):
    watcher = None
    watch_handlers = None
    watch_excludes = None
    watch_includes = None
    filter_match = None

    def __init__(self, filename, dict_type=DictNode, list_type=list, opener=open, watcher=None, watcher_type=Observer,
                 filter_key=None):
        self.filename = filename
        self.dict_type = dict_type
        self.list_type = list_type
        self.opener = opener
        self.line_cursor = 0
        self.indent_size = 0
        self.current_key = None
        self.stack = [(str, dict_type())]
        self.multiline_capture = None
        self.filter_key = filter_key

        if watcher:
            self.watcher = watcher
        elif watcher_type:
            self.watcher = watcher_type()

        if self.watcher and self.watch_handlers is None:
            self.watch_handlers = {}

        if self.watcher and self.watch_excludes is None:
            self.watch_excludes = {}

        if self.watcher and self.watch_includes is None:
            self.watch_includes = {}

        globals().update(here=abspath(dirname(filename)))
        with opener(filename) as f:
            for l in f:
                self.line_cursor += 1
                self.parse_line(l)

    def reload(self, filter_key=None):
        if self.watcher and filter_key and filter_key in self.watch_handlers:
            for w in self.watch_handlers[filter_key]:
                try:
                    self.watcher.unschedule(w)
                except KeyError:
                    continue

            self.watch_excludes[filter_key] = set()
            self.watch_includes[filter_key] = set()

        self.__init__(
            self.filename,
            dict_type=self.dict_type,
            list_type=self.list_type,
            opener=self.opener,
            watcher_type=None,
            watcher=self.watcher,
            filter_key=filter_key
        )

    def get_filter_key(self):
        return None if self.level <= 0 else self.stack[-1][0]

    def watch(self, path, recursive=False):
        if self.watcher is None or not self.is_active:
            return

        filter_key = self.get_filter_key()

        handlers = self.watch_handlers.setdefault(filter_key, [])

        path = abspath(path)
        if not isdir(path):
            included_files = self.watch_includes.setdefault(filter_key, set())
            included_files.add(path)

        handlers.append(self.watcher.schedule(
            WatcherEventHandler(self, filter_key=filter_key),
            dirname(path),
            recursive=recursive,
        ))

    def exclude_watch(self, path):
        if self.watcher is None or not self.is_active:
            return
        filter_key = self.get_filter_key()
        excluded_files = self.watch_excludes.setdefault(filter_key, set())
        excluded_files.add(abspath(path))

    @property
    def current(self):
        return self.stack[-1][1]

    @property
    def level(self):
        return len(self.stack) - 1

    @property
    def root(self):
        return self.stack[0][1]

    def last_dict(self):
        for key, node in self.stack[::-1]:
            if isinstance(node, dict):
                return node

    def parse_value(self, v):

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
            if not v.strip():
                return None

        if INTEGER_PATTERN.match(v):
            return int(v)
        elif FLOAT_PATTERN.match(v):
            return float(v)
        else:
            return eval('f"""%s"""' % v, globals(), self.last_dict())

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
                if not line.strip() or COMMENT_PATTERN.match(line):
                    return

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
                    self.stack.append((parent_key, self.current[parent_key]))
                else:
                    while self.level > level:
                        # backward
                        self.stack.pop()

                if self.filter_match and self.filter_match > self.level:
                    self.filter_match = None

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
                    self.echo(value)
                elif key == 'PY':
                    self.py_exec(value)
                elif key == 'WATCH':
                    self.watch(value)
                elif key == 'WATCH-ALL':
                    self.watch(value, recursive=True)
                elif key == 'NO-WATCH':
                    self.exclude_watch(value)
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

            if self.filter_key == key:
                self.filter_match = self.level + 1

            self.current_key = key
        except MultiLineValueDetected:
            if key:
                self.current_key = key
            return

    @property
    def is_active(self):
        return self.filter_key is None or self.filter_match

    def echo(self, msg):
        if not self.is_active:
            return
        print(msg)

    def py_exec(self, statement):
        if not self.is_active:
            return
        exec(statement, globals(), self.last_dict())

    def shell(self, cmd):
        if not self.is_active:
            return

        # ON error: It will be printed on stderr, so just suppressing the execution is enough.
        subprocess.run(cmd, shell=True, check=True)

    def wait_for_changes(self):  # pragma: no cover
        self.watcher.start()
        self.watcher.join()

    def compile_sass(self, params):
        if not self.is_active:
            return

        if libsass is None:  # pragma: no cover
            raise ImportError(
                'In order, to use `SASS` tags, please install the `libsass` using: `pip install libsass`',
                name='libsass',
            )
        src, dst = params.split('>') if '>' in params else params.split(' ')
        src, dst = src.strip(), dst.strip()
        with open(dst, 'w') as f:
            f.write(libsass.compile(filename=src))


def quickstart(filename, watch=False):  # pragma: no cover
    p = Project(filename, watcher_type=Observer if watch else None)
    if watch:
        return p.wait_for_changes()


def main():  # pragma: no cover
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


if __name__ == '__main__':  # pragma: no cover
    import sys
    sys.exit(main())
