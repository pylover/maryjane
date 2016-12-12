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
import sys
import time
import traceback
import threading
import subprocess
from datetime import datetime, timedelta
from os.path import abspath, dirname, isdir

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    # noinspection PyPackageRequirements
    import sass as libsass
except ImportError:  # pragma: no cover
    libsass = None


__version__ = '4.4.5'


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
        src_path = abspath(event.src_path)
        src_dir = dirname(src_path)

        for path in self.project.watch_excludes.get(self.filter_key, []):
            if (isinstance(path, str) and (src_path == path or src_dir == path)) or \
                    (hasattr(path, 'match') and path.match(src_path)):
                self.project.debug('CHANGED (IGNORED):', src_path)
                return

        for path in self.project.watch_includes.get(self.filter_key, []):
            include_dir = abspath(dirname(path))
            if (isinstance(path, str) and (src_dir == include_dir and src_path not in path)) or \
                    (hasattr(path, 'match') and not path.match(src_path)):
                self.project.debug('CHANGED (IGNORED):', src_path)
                return

        self.project.debug('CHANGED:', src_path)
        self.project.record_a_change(self.filter_key)


class MultiLineValueDetected(Exception):
    pass


class Project(object):
    watcher = None
    watch_handlers = None
    watch_excludes = None
    watch_includes = None
    filter_match = None

    def __init__(self, filename, dict_type=DictNode, list_type=list, opener=open, watcher=None, watcher_type=Observer,
                 filter_keys=None, watch_delay=.5, debug=False):
        self.filename = filename
        self.dict_type = dict_type
        self.list_type = list_type
        self.opener = opener
        self.line_cursor = 0
        self.indent_size = 0
        self.current_key = None
        self.stack = [('ROOT', dict_type())]
        self.multiline_capture = None
        self.filter_keys = filter_keys
        self._change_lock = threading.Lock()
        self.changes = set()
        self.dirty = None
        self.watch_delay = watch_delay
        self._debug = debug

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

    def debug(self, *args):
        if self._debug:
            print(*args)

    def _unschedule_watch(self, *filter_keys):
        for filter_key in filter_keys:
            for w in self.watch_handlers[filter_key]:
                try:
                    self.watcher.unschedule(w)
                except KeyError:  # pragma: no cover
                    continue
            self.watch_handlers[filter_key] = []
            self.watch_excludes[filter_key] = set()
            self.watch_includes[filter_key] = set()

    def reload(self, filter_keys: set=None):
        if self.watcher and filter_keys and filter_keys.intersection(self.watch_handlers.keys()):
            self._unschedule_watch(*filter_keys)
        else:
            for k in self.watch_handlers or {}:
                self._unschedule_watch(k)

        self.__init__(
            self.filename,
            dict_type=self.dict_type,
            list_type=self.list_type,
            opener=self.opener,
            watcher_type=None,
            watcher=self.watcher,
            filter_keys=filter_keys,
            watch_delay=self.watch_delay,
            debug=self._debug
        )

    def get_watch_filter_key(self):
        if self.level <= 0:
            return None

        key = self.stack[-1][0]
        if 'WATCH' in key:
            if self.level > 1:
                return self.stack[-2][0]
            else:
                return None

        return key

    @staticmethod
    def prepare_path_for_watch(path):
        regex = None
        if path.startswith('!'):
            regex = re.compile(path[1:])
            path = globals().get('here')
        else:
            path = abspath(path)
        return path, regex

    def watch(self, path, recursive=False):
        if self.watcher is None or not self.is_active:
            return

        path, regex = self.prepare_path_for_watch(path)
        filter_key = self.get_watch_filter_key()
        handlers = self.watch_handlers.setdefault(filter_key, [])

        if not isdir(path):
            included_files = self.watch_includes.setdefault(filter_key, set())
            included_files.add(regex or path)

        handlers.append(self.watcher.schedule(
            WatcherEventHandler(self, filter_key=filter_key),
            path if isdir(path) else dirname(path),
            recursive=recursive,
        ))

    def exclude_watch(self, path):
        if self.watcher is None or not self.is_active:
            return
        path, regex = self.prepare_path_for_watch(path)
        filter_key = self.get_watch_filter_key()
        excluded_files = self.watch_excludes.setdefault(filter_key, set())
        excluded_files.add(regex or abspath(path))

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
            if COMMENT_PATTERN.match(line):
                return

            if self.multiline_capture is not None:
                line_data = self.indent_size * self.level, self.current_key, \
                            self.parse_value(line[(self.level + 1) * self.indent_size:])
            else:
                if not line.strip():
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
                elif key == 'SHELL-INTO':
                    self.shell_into(value)
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

            if self.filter_keys and key in self.filter_keys:
                self.filter_match = self.level + 1

            self.current_key = key
        except MultiLineValueDetected:
            if key:
                self.current_key = key
            return

    @property
    def is_active(self):
        return not self.filter_keys or self.filter_match

    def echo(self, msg):
        if not self.is_active:
            return
        print(msg)

    def py_exec(self, statement):
        if not self.is_active:
            return
        exec(statement, globals(), self.last_dict())

    @staticmethod
    def popen(*args, **kwargs) -> (str, str):
        process = subprocess.Popen(*args, shell=True, **kwargs)
        stdout, stderr = process.communicate()
        process.wait()
        exit_code = process.poll()
        if exit_code:
            raise subprocess.CalledProcessError(exit_code, args[0], output=stdout, stderr=stderr)
        return stdout, stderr

    def shell(self, cmd):
        if not self.is_active:
            return

        self.popen(cmd)

    def shell_into(self, cmd):
        if not self.is_active:
            return

        words = cmd.split(' ')
        key, cmd = words[0], ' '.join(words[1:])

        stdout, stderr = self.popen(cmd, universal_newlines=True, stdout=subprocess.PIPE)
        self.current[key] = stdout

    def record_a_change(self, filter_key):
        with self._change_lock:
            if not self.dirty:
                self.dirty = datetime.now()

            self.changes.add(filter_key)

    def wait_for_changes(self):  # pragma: no cover
        self.watcher.start()
        while True:
            if self.dirty and (datetime.now() - self.dirty > timedelta(seconds=self.watch_delay)):
                self.debug('RELOADING: ', self.changes)
                with self._change_lock:
                    if None in self.changes:
                        self.reload()
                    else:
                        self.reload(self.changes)
            else:
                time.sleep(self.watch_delay / 2)

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
        try:
            with open(dst, 'w') as f:
                f.write(libsass.compile(filename=src))
        except libsass.CompileError:
            traceback.print_exc()


def quickstart(filename, watch=False, **kw):  # pragma: no cover
    p = Project(filename, watcher_type=Observer if watch else None, **kw)
    if watch:
        return p.wait_for_changes()


def main():  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description='File watcher and task manager')
    parser.add_argument('manifest', nargs='?', default='maryjane.yml', help='Manifest file, default: "maryjane.yml"')
    parser.add_argument('-w', '--watch', action='store_true',
                        help='Watch for modifications, and execute tasks if needed.')
    parser.add_argument('-d', '--watch-delay', default=.5, type=float,
                        help='Seconds to wait before reloading the project after change(s) detected, It gives a chance '
                             'to gather all changes before reload, to prevent multiple reloads in a short mather of '
                             'time.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose.')
    parser.add_argument('-V', '--version', action='store_true', help='Show version.')

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    try:
        return quickstart(args.manifest, watch=args.watch, watch_delay=args.watch_delay, debug=args.verbose)
    except FileNotFoundError:
        print(
            "No such file: 'maryjane.yml', You must have a `maryjane.yml` in the current directory or specify a "
            "manifest filename.", file=sys.stderr)
        parser.print_help()
    except KeyboardInterrupt:
        print('CTRL+C detected.')
        return 1


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
