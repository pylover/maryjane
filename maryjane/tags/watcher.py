# -*- coding: utf-8 -*-
from maryjane.tags.base import DictionaryTag
__author__ = 'vahid'


class WatcherTag(DictionaryTag):
    recursive = False
    strict = True
    predicate = None

    def __repr__(self):
        return '<WatcherTag>'

