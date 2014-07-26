# -*- coding: utf-8 -*-
from maryjane.tags import LazyTag
from mako.template import Template as MakoTemplate
__author__ = 'vahid'


class TemplateTag(LazyTag, MakoTemplate):

    def __init__(self, manifest, *args, **kwargs):
        LazyTag.__init__(self, manifest)
        MakoTemplate.__init__(self, *args, **kwargs)

    def get_value(self):
        return self.render(**self.manifest.context)

    @classmethod
    def from_yaml_node(cls, manifest, loader, node):
        template = loader.construct_scalar(node)
        return cls(manifest, template)

    def __repr__(self):
        return '<TemplateTag "%s">' % self.source

