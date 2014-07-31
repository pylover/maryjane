# -*- coding: utf-8 -*-
from maryjane.tags import LazyScalarTag
from mako.template import Template as MakoTemplate
__author__ = 'vahid'


class TemplateTag(LazyScalarTag, MakoTemplate):

    def __init__(self, template, manifest):
        LazyScalarTag.__init__(self, template, manifest)
        MakoTemplate.__init__(self, self.value, strict_undefined=True)

    def lazy_value(self):
        return self.render(**self.manifest.context)


    def __repr__(self):
        return '<TemplateTag "%s">' % self.source

