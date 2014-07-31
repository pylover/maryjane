# -*- coding: utf-8 -*-
from maryjane.tags.base import DictionaryTag


__author__ = 'vahid'

class ActionTag(DictionaryTag):

    def execute(self):
        if hasattr(self, 'banner'):
            print self.banner

    def __repr__(self):
        return '<ActionTag>'

