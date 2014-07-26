# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

__author__ = 'vahid'


class BaseTag(object):
    __metaclass__ = ABCMeta

    def __init__(self, manifest, **attributes):
        self.manifest = manifest
        self.__dict__.update(attributes)

    def __getattribute__(self, item):
        v = object.__getattribute__(self, item)
        if isinstance(v, LazyTag):
            return v.get_value()
        return v

    @classmethod
    def from_yaml_node(cls, manifest, loader, node):
        kw = loader.construct_mapping(node)
        return cls(manifest, **kw)


class LazyTag(BaseTag):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_value(self, context):
        pass