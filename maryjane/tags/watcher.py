# -*- coding: utf-8 -*-
from maryjane.tags import BaseTag
__author__ = 'vahid'


class WatcherTag(BaseTag):
    recursive = False
    strict = True
    predicate = None

    def __repr__(self):
        return '<WatcherTag>'

