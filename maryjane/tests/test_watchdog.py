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
        self.out_file = os.path.join(thisdir,'out.js')
        with open(self.test_source_file,'w') as f:
            f.write('\n// something \n')
 
    def test_observer(self):
        # removing output file to do a clean test
        if os.path.exists(self.out_file):
            os.remove(self.out_file)
        
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
        
        self.assertTrue(os.path.exists(self.out_file))
         
        observer.stop()
        observer.join()
         
if __name__ == "__main__":
    unittest.main()        