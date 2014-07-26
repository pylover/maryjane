# -*- coding: utf-8 -*-
from maryjane.tags import LazyScalarTag
__author__ = 'vahid'


class EvaluateTag(LazyScalarTag):
    def __init__(self, raw_value, manifest):
        super(EvaluateTag, self).__init__(raw_value ,manifest)

    def lazy_value(self):
        return eval(self.value, self.manifest.context)

