# -*- coding: utf-8 -*-
'''
Created on:    Apr 1, 2014
@author:        vahid
'''
import unittest
import os.path
from maryjane import Manifest

thisdir = os.path.dirname(__file__)

class TestManifest(unittest.TestCase):
    
    def setUp(self):
        self.manifest_file = os.path.join(thisdir,'test.manifest')
        
    def test_manifest(self):
        m = Manifest(self.manifest_file)
        
        watches = list(m.get_task_names())
        self.assertEqual(len(watches), 2)
        self.assertEqual(watches[0], 'test')
        self.assertEqual(watches[1], 'minify_test')
        
        
        self.assert_(m.test.output.endswith('out.js'))
        self.assertEqual(len(m.test.sources), 2)
        self.assert_(m.test.sources[0].endswith('a.js'))
        self.assert_(m.test.sources[1].endswith('b.js'))
        
        
        
            
            
if __name__ == "__main__":
    unittest.main()
