# -*- coding: utf-8 -*-
'''
Created on:    Apr 1, 2014
@author:        vahid
'''
from pymlconf import ConfigManager
import os.path 


class Manifest(ConfigManager):
    def __init__(self,manifest_file):
        ConfigManager.__init__(self, files=manifest_file)
        manifest_dir = os.path.dirname(manifest_file)
        for key in self.get_task_names():
            self[key].sources = [i if i.startswith('/') else os.path.abspath(os.path.join(manifest_dir, i)) for i in self[key].sources]

            if isinstance(self[key].output, basestring) and not self[key].output.startswith('/'):
                self[key].output = os.path.abspath(os.path.join(manifest_dir, self[key].output))
            else:
                for out_type, filename in self[key].output.iteritems():
                    if not filename.startswith('/'):
                        self[key].output[out_type] = os.path.abspath(os.path.join(manifest_dir, filename))

    
    def get_task_names(self):
        for k in self.keys():
            if isinstance(k,basestring) and not k.startswith('_'):
                yield k