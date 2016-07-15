# -*- coding: utf-8 -*-
from __future__ import print_function

import yaml
import time
import os.path
import traceback
from collections import OrderedDict
from watchdog.observers import Observer
from maryjane.tags import TaskTag, SubprocessActionTag, TemplateTag, ObservableTaskTag,\
    EvaluateTag, OptionsTag, WatcherTag, ImportTag, BannerActionTag, ContextTag
from maryjane.helpers import get_source_dirs, has_file_overlap, split_paths, get_filename
from watchdog.events import FileSystemEventHandler


class ManifestFileEventHandler(FileSystemEventHandler):
    def __init__(self, manifest):
        self.manifest = manifest
        super(FileSystemEventHandler, self).__init__()

    def on_any_event(self, event):
        paths = []
        if hasattr(event, 'src_path'):
            paths += split_paths(event.src_path)
        if hasattr(event, 'dest_path'):
            paths += split_paths(event.dest_path)

        if has_file_overlap(paths, self.manifest.filename):
            # noinspection PyBroadException
            try:
                self.manifest.reboot()
            except:
                traceback.print_exc()

_context_builtins = {
    'has_file_overlap': has_file_overlap,
    'split_paths': split_paths,
    'get_source_dirs': get_source_dirs,
    'get_filename': get_filename
}


class ManifestObserver(Observer):

    def __init__(self, manifest):
        self.manifest = manifest
        Observer.__init__(self)
        self.schedule(ManifestFileEventHandler(self.manifest),
                      get_source_dirs(self.manifest.filename)[0])

    def run(self):
        print("Starting Manifest Watcher")
        self.manifest.watch()
        super(ManifestObserver, self).run()


class Manifest(object):

    def __init__(self, filename, working_dir='.'):
        self.filename = filename
        self.working_dir = working_dir
        self.configure_yaml()
        self.tasks = {}
        self.watching_tasks = {}
        self._context = {}
        self.observer = None
        self.is_watching = False
        self.reload_file()

    def reboot(self):
        self.unwatch()
        self.reload_file()
        self.execute()
        self.watch()

    def reload_file(self):
        manifest_dir = os.path.dirname(self.filename)
        self._context = dict(
            manifest_dir='.' if not manifest_dir else manifest_dir,
            working_dir=self.working_dir
        )

        self._context.update(_context_builtins)
        with open(self.filename) as manifest_file:
            config = yaml.load(manifest_file)

        self.tasks = OrderedDict(sorted([(k, v) for k, v in config.items() if isinstance(v, TaskTag)],
                                        key=lambda i: i[1].priority))

        self.watching_tasks = {k: v for k, v in config.items() if isinstance(v, ObservableTaskTag)}
        self._context.update(self.tasks)

    def __getattr__(self, name):
        if name in self.tasks:
            return self.tasks[name]
        raise AttributeError

    @property
    def context(self):
        return self._context

    def execute(self):
        for task_name, task in self.tasks.items():
            task.execute_actions()

    def configure_yaml(self):
        def specialize(func):
            def _decorator(*args, **kwargs):
                return func(self, *args, **kwargs)
            return _decorator
        yaml.add_constructor('!options', specialize(OptionsTag.from_yaml_node))
        yaml.add_constructor('!subprocess', specialize(SubprocessActionTag.from_yaml_node))
        yaml.add_constructor('!task', specialize(TaskTag.from_yaml_node))
        yaml.add_constructor('!watch', specialize(ObservableTaskTag.from_yaml_node))
        yaml.add_constructor('!template', specialize(TemplateTag.from_yaml_node))
        yaml.add_constructor('!eval', specialize(EvaluateTag.from_yaml_node))
        yaml.add_constructor('!watcher', specialize(WatcherTag.from_yaml_node))
        yaml.add_constructor('!import', specialize(ImportTag.from_yaml_node))
        yaml.add_constructor('!banner', specialize(BannerActionTag.from_yaml_node))
        yaml.add_constructor('!context', specialize(ContextTag.from_yaml_node))

    def unwatch(self):
        if self.observer.is_alive():
            self.observer.stop()

    def watch(self):
        self.observer = Observer()
        for task_name, task in self.watching_tasks.items():
            handler = task.create_event_handler()
            for directory in get_source_dirs(task.watcher.sources):
                self.observer.schedule(handler, directory, recursive=task.watcher.recursive)
        print("Starting Task Watcher")
        self.observer.start()


if __name__ == '__main__':
    fn = 'tests/maryjane.yaml'
    m = Manifest(fn, working_dir='tests')
    m.execute()
    o = ManifestObserver(m)
    o.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            o.stop()
            o.join()
            break
