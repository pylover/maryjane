# -*- coding: utf-8 -*-
'''
Created on:    Apr 1, 2014
@author:        vahid
'''
import unittest
import os.path
from maryjane import Builder, Manifest

thisdir = os.path.dirname(__file__)

class TestBuilder(unittest.TestCase):
    
    def setUp(self):
        self.manifest_file = os.path.join(thisdir,'test.manifest')
        
    def test_builder(self):
        m = Manifest(self.manifest_file)
        
        taskes = list(m.get_task_names())
        self.assertEqual(len(taskes), 2)
        self.assertEqual(taskes[0], 'test')
        
        builder = Builder(m['test'])
        builder.do_()
        
        self.assertTrue(os.path.exists(m.test.output))
        
        
        
        
        
            
            
if __name__ == "__main__":
    unittest.main()
