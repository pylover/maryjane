# -*- coding: utf-8 -*-
from maryjane.tags import LazyScalarTag
import importlib
__author__ = 'vahid'


class ImportTag(LazyScalarTag):
    def __init__(self, raw_value, manifest):
        super(ImportTag, self).__init__(raw_value ,manifest)

    def lazy_value(self):
        if 'from' in self.value:
            module_name, from_ = [v.strip() for v in self.value.split('from')]
            module = importlib.import_module(module_name)
            if module and hasattr(module, from_):
                return getattr(module, from_)
            raise ImportError('Cannot import %s' % self.value)
        else:
            return importlib.import_module(self.value)
