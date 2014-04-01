# -*- coding: utf-8 -*-
'''
Created on:    Nov 10, 2013
@author:        vahid
'''
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from maryjane import Builder
from maryjane import Manifest
from maryjane.helpers import get_source_dirs , split_paths, check_overlap


class MaryJaneEventHandler(FileSystemEventHandler):
    def __init__(self,task):
        self.task = task
        self.builder = Builder(self.task)
        super(FileSystemEventHandler, self).__init__()
          
    def on_any_event(self,event):
        paths = []
        if hasattr(event,'src_path'):
            paths += split_paths(event.src_path)
        if hasattr(event,'dest_path'):
            paths += split_paths(event.dest_path)
       
        if len(paths) and check_overlap(paths, self.task.sources, lambda a,b: a == b):
            self.builder.do_()

class MaryJaneObserver(Observer):
    def __init__(self,manifest_file):
        Observer.__init__(self)
        self.manifest_file = manifest_file
        self.reload_manifest()
        
    def add_watch(self,task):
        dirs = get_source_dirs(task.sources)
        handler = MaryJaneEventHandler(task)
        handler.builder.do_()
        for d in dirs:
            self.schedule(handler, d, recursive=False)
        
    def reload_manifest(self):
        manifest = Manifest(self.manifest_file)
        for taskname in manifest.get_task_names():
            self.add_watch(manifest[taskname])
            
        
    
