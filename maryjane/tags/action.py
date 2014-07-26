# -*- coding: utf-8 -*-
from maryjane.tags import BaseTag
import subprocess as sb
__author__ = 'vahid'

class ActionTag(BaseTag):

    def __repr__(self):
        return '<ActionTag>'

class SubprocessActionTag(ActionTag):

    def __init__(self, manifest, popen_args, **attributes):
        self.popen_args = popen_args
        super(SubprocessActionTag, self).__init__(manifest, **attributes)

    @classmethod
    def from_yaml_node(cls, manifest, loader, node):
        kw = loader.construct_mapping(node)

        arguments = kw.get('arguments')
        if 'arguments' in kw:
            del kw['arguments']

        return cls(manifest, kw, **dict(arguments=arguments))

    def execute(self):
        p = sb.Popen(self.arguments, **self.popen_args)
        p.wait()

    def __repr__(self):
        return '<SubprocessActionTag %s>' % self.executable

