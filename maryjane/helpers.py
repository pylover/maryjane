# -*- coding: utf-8 -*-
'''
Created on:    Nov 10, 2013
@author:        vahid
'''
import os
import glob

def distinct(l):
    if not l or not len(l):
        return []
    return list(set(l))

def get_source_dirs(sources):
    source_dirs = []
    for s in sources:
        if os.path.isdir(s):
            source_dirs.append(s)
        else:
            p = os.path.abspath(os.path.dirname(s))
            if os.path.isdir(p):
                source_dirs.append(p)
            
    return sorted(distinct(source_dirs))

def split_paths(p):
    if isinstance(p, basestring):
        res = p.split(',')
    else:
        res = p
    return [os.path.abspath(i.strip()) for i in res ]

def check_overlap(arr1,arr2, checker):
    for i1 in arr1:
        for i2 in arr2:
            res = checker(i1,i2)
            if res:
                return res
    return False
