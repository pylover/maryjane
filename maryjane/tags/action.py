# -*- coding: utf-8 -*-
from __future__ import print_function

from maryjane.tags.base import DictionaryTag


class ActionTag(DictionaryTag):

    def execute(self):
        if hasattr(self, 'banner') and self.banner.strip():
            print(self.banner)

    def __repr__(self):
        return '<ActionTag>'
