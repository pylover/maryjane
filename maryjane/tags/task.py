# -*- coding: utf-8 -*-
from maryjane.tags.base import DictionaryTag
from maryjane.helpers import split_paths
from watchdog.events import FileSystemEventHandler
import traceback


class TaskTag(DictionaryTag):
    priority = 50

    def __init__(self, manifest, **attributes):
        if 'priority' in attributes:
            attributes['priority'] = int(attributes['priority'])
        super(TaskTag, self).__init__(manifest, **attributes)

    def execute_actions(self):
        if hasattr(self, 'banner'):
            print(self.banner)
        for action in self.actions:
            action.execute()

    def __repr__(self):
        return '<TaskTag>'


class TaskEventHandler(FileSystemEventHandler):
    def __init__(self, task):
        self.task = task
        super(FileSystemEventHandler, self).__init__()

    def on_any_event(self, event):
        # noinspection PyBroadException
        try:
            self.task.execute_if_needed(event)
        except:
            traceback.print_exc()


class ObservableTaskTag(TaskTag):

    def execute_if_needed(self, event):
        update_needed = False
        paths = []
        if hasattr(event, 'src_path'):
            paths += split_paths(event.src_path)
        if hasattr(event, 'dest_path'):
            paths += split_paths(event.dest_path)

        if self.watcher.predicate:
            for p in paths:
                if self.watcher.predicate(p):
                    update_needed = True
                    break
        else:
            update_needed = True

        if update_needed:
            self.execute_actions()

    def create_event_handler(self):
        return TaskEventHandler(self)

    def __repr__(self):
        return '<ObservableTaskTag>'
