# -*- coding: utf-8 -*-
from maryjane.tags.base import DictionaryTag

__author__ = 'vahid'


class ContextTag(DictionaryTag):
    def __init__(self, manifest, **attributes):
        super(ContextTag, self).__init__(manifest, **attributes)
        manifest.context.update(attributes)
        manifest.context.update(self.to_dict())
