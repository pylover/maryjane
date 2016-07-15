# -*- coding: utf-8 -*-

from maryjane.tags.action import ActionTag
from maryjane.tags.options import OptionsTag
import subprocess as sb

__author__ = 'vahid'
class SubprocessActionTag(ActionTag):
    echo = False

    def __init__(self, manifest, popen_args, **attributes):
        self.popen_args = popen_args
        super(SubprocessActionTag, self).__init__(manifest, **attributes)

    @classmethod
    def from_yaml_node(cls, manifest, loader, node):
        kw = loader.construct_mapping(node)

        class_kwargs = {}
        for arg_name in ('arguments', 'banner', 'echo'):
            arg_value = kw.get(arg_name)
            if arg_value:
                class_kwargs[arg_name] = arg_value

            if arg_name in kw:
                del kw[arg_name]

        popen_args = OptionsTag(manifest, **kw)

        return cls(manifest, popen_args, **class_kwargs)

    def execute(self):
        super(SubprocessActionTag, self).execute()
        args = self.popen_args.to_dict()
        if 'manifest' in args:
            del args['manifest']
        if self.echo:
            print('Executing: %s' % self.arguments)
        p = sb.Popen(self.arguments, **args)
        p.wait()

    def __repr__(self):
        return '<SubprocessActionTag %s>' % self.executable

