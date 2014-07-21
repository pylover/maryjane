# -*- coding: utf-8 -*-
"""
Created on:    Nov 1, 2013
@author:        vahid
"""
from rjsmin import jsmin as minify


class Builder(object):
    def __init__(self,task):
        self.task = task

    def _get_outputs(self):
        if isinstance(self.task.output, basestring):
            return {'normal': self.task.output}
        return self.task.output

    def do_(self):
        outputs = self._get_outputs()
        try:
            out_files = [None if k not in outputs else open(outputs[k], 'w') for k in ('normal', 'minified')]
            normal_file, minified_file = out_files

            for out_type, filename in outputs.iteritems():
                print "Writing (%s) %s" % (out_type, filename)

            for source_filename in self.task.sources:
                with open(source_filename) as source_file:
                    content = source_file.read()
                    if normal_file:
                        normal_file.write(content)
                    if minified_file:
                        minified_file.write(minify(content))

        finally:
            if normal_file:
                normal_file.close()

            if minified_file:
                minified_file.close()

