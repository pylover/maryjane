# -*- coding: utf-8 -*-
import yaml
import time
import os.path
from watchdog.observers import Observer
from maryjane.tags import TaskTag, SubprocessActionTag, TemplateTag, ObservableTaskTag, EvaluateTag, OptionsTag
from maryjane.helpers import get_source_dirs

__author__ = 'vahid'

class Manifest(object):

    def __init__(self, filename, working_dir='.'):
        self.filename = filename
        self.configure_yaml()
        manifest_dir = os.path.dirname(self.filename)

        self._context = dict(manifest_dir= '.' if not manifest_dir else manifest_dir,
                             working_dir=working_dir)
        with open(filename) as manifest_file:
            config = yaml.load(manifest_file)
        self.tasks = {k: v for k, v in config.iteritems() if isinstance(v, TaskTag)}
        self.watching_tasks = {k: v for k, v in config.iteritems() if isinstance(v, ObservableTaskTag)}
        if 'context' in config:
            self._context.update(config['context'].to_dict())
            self._context.update(self.tasks)

    def __getattr__(self, name):
        if name in self.tasks:
            return self.tasks[name]
        raise AttributeError

    @property
    def context(self):
        return self._context

    def execute(self):
        for task_name, task in self.tasks.iteritems():
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

    def watch(self, block=False):
        observer = Observer()
        for task_name, task in self.watching_tasks.iteritems():
            for directory in get_source_dirs(task.watch):
                observer.schedule(task.create_event_handler(), directory)

        observer.start()
        if block:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

if __name__ == '__main__':
    fn = 'tests/maryjane.yaml'
    m = Manifest(fn, working_dir='tests')

    m.execute()
    m.watch(block=True)

