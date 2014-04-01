# -*- coding: utf-8 -*-
'''
Created on:    Nov 1, 2013
@author:        vahid
'''

class Builder(object):
    def __init__(self,task):
        self.task = task

    def do_(self):
        print "Writing to %s" % self.task.output
        with open(self.task.output,'w') as outfile:
            for sourcefile in self.task.sources:
                self._import_one(outfile,sourcefile)
        return self
            
    def _import_one(self,stream,sourcefile):
        print "Reading %s" % sourcefile
        with open(sourcefile) as source_file:
            for line in source_file:
                stream.write(line)