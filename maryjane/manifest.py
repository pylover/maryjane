# -*- coding: utf-8 -*-
import yaml

from maryjane.tags import TaskTag, SubprocessActionTag, TemplateTag

__author__ = 'vahid'

class Manifest(object):
    def __init__(self):
        self.tasks = {}

    def __getattr__(self, name):
        if name in self.tasks:
            return self.tasks[name]
        raise AttributeError

    @property
    def context(self):
        return self.tasks

    def execute(self):
        """
        Executes all tasks
        :return: void
        """
        for task_name, task in self.tasks.iteritems():
            print 'Executing task: %s' % task_name
            task.execute_actions()

    def load(self, stream):
        def specialize(func):
            def _decorator(*args, **kwargs):
                return func(self, *args, **kwargs)
            return _decorator

        yaml.add_constructor('!subprocess', specialize(SubprocessActionTag.from_yaml_node))
        yaml.add_constructor('!task', specialize(TaskTag.from_yaml_node))
        yaml.add_constructor('!template', specialize(TemplateTag.from_yaml_node))
        config = yaml.load(stream)
        self.tasks.update({k: v for k, v in config.iteritems() if isinstance(v, TaskTag)})


if __name__ == '__main__':
    fn = 'tests/maryjane.yaml'
    m = Manifest()
    with open(fn) as f:
        m.load(f)

    m.execute()

