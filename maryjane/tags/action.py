# -*- coding: utf-8 -*-
from maryjane.tags import BaseTag, OptionsTag
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

        popen_args = OptionsTag(manifest, **kw)

        return cls(manifest, popen_args, **dict(arguments=arguments))

    def execute(self):
        args = self.popen_args.to_dict()
        if 'manifest' in args:
            del args['manifest']
        p = sb.Popen(self.arguments, **args)
        p.wait()

    def __repr__(self):
        return '<SubprocessActionTag %s>' % self.executable

