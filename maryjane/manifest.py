# -*- coding: utf-8 -*-
import yaml
import time
from watchdog.observers import Observer
from maryjane.tags import TaskTag, SubprocessActionTag, TemplateTag, ObservableTaskTag, EvaluateTag
from maryjane.helpers import get_source_dirs

__author__ = 'vahid'

class Manifest(object):

    def __init__(self, working_dir='.'):
        self.working_dir = working_dir
        self.tasks = {}
        self.watching_tasks = {}
        self.configure_yaml()

    def __getattr__(self, name):
        if name in self.tasks:
            return self.tasks[name]
        raise AttributeError

    @property
    def context(self):
        ctx = self.tasks.copy()
        ctx.update({'working_dir': self.working_dir})
        return ctx

    def execute(self):
        for task_name, task in self.tasks.iteritems():
            task.execute_actions()

    def configure_yaml(self):
        def specialize(func):
            def _decorator(*args, **kwargs):
                return func(self, *args, **kwargs)
            return _decorator
        yaml.add_constructor('!subprocess', specialize(SubprocessActionTag.from_yaml_node))
        yaml.add_constructor('!task', specialize(TaskTag.from_yaml_node))
        yaml.add_constructor('!watch', specialize(ObservableTaskTag.from_yaml_node))
        yaml.add_constructor('!template', specialize(TemplateTag.from_yaml_node))
        yaml.add_constructor('!eval', specialize(EvaluateTag.from_yaml_node))

    def load(self, stream):
        config = yaml.load(stream)
        self.tasks.update({k: v for k, v in config.iteritems() if isinstance(v, TaskTag)})
        self.watching_tasks.update({k: v for k, v in config.iteritems() if isinstance(v, ObservableTaskTag)})


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
    m = Manifest(working_dir='tests')
    with open(fn) as f:
        m.load(f)

    m.execute()
    m.watch(block=True)

