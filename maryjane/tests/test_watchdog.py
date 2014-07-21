# -*- coding: utf-8 -*-
'''
Created on Nov 1, 2013

@author: vahid
'''
import unittest
import os
import time
from maryjane import MaryJaneObserver

thisdir = os.path.dirname(__file__)
 
class TestWatchdog(unittest.TestCase):
     
    def setUp(self):
        self.watch_dir = os.path.join(os.path.dirname(__file__),'watch_dir')
        if not os.path.exists(self.watch_dir):
            os.mkdir(self.watch_dir)
        self.test_source_file = os.path.join(os.path.dirname(__file__),'watch_dir','a.js')
        self.manifest_file = os.path.join(thisdir,'test.manifest')
        self.out_files = [
            os.path.join(thisdir,'out.js'),
            os.path.join(thisdir,'minify_test.js'),
            os.path.join(thisdir,'minify_test.min.js')]

        with open(self.test_source_file,'w') as f:
            f.write('\n// something \n')
 
    def test_observer(self):
        # removing output file to do a clean test
        for f in self.out_files:
            if os.path.exists(f):
                os.remove(f)
        
        # creating and starting observer
        observer = MaryJaneObserver(self.manifest_file)
        observer.start()
        
        # wait some moments to initialize observer thread
        time.sleep(.5)
        
        # append something to source file
        with open(self.test_source_file,'a') as f:
            f.write("""
alert('something');
""")
 
        # wait additional moments to write the out file
        time.sleep(.5)

        for f in self.out_files:
            self.assertTrue(os.path.exists(f))
         
        observer.stop()
        observer.join()
         
if __name__ == "__main__":
    unittest.main()        