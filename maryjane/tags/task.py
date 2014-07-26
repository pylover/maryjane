# -*- coding: utf-8 -*-
from maryjane.tags import BaseTag
__author__ = 'vahid'


class TaskTag(BaseTag):

    def execute_actions(self):
        for action in self.actions:
            action.execute()

    def __repr__(self):
        return '<TaskTag>'

class ObservableTaskTag(TaskTag):
    def __repr__(self):
        return '<ObservableTaskTag>'
