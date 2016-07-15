# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class BaseTag(object):
    __metaclass__ = ABCMeta

    def __init__(self, manifest, **kw):
        self.manifest = manifest

    def __getattribute__(self, item):
        v = object.__getattribute__(self, item)
        if isinstance(v, LazyTag):
            return v.lazy_value()
        elif isinstance(v, list):
            return [i if not isinstance(i, LazyTag) else i.lazy_value() for i in v]
        return v


class DictionaryTag(BaseTag):

    def __init__(self, manifest, **attributes):
        super(DictionaryTag, self).__init__(manifest)
        self.__dict__.update(attributes)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dict__ if not k.startswith('_')}

    @classmethod
    def from_yaml_node(cls, manifest, loader, node):
        kw = loader.construct_mapping(node)
        return cls(manifest, **kw)

    def __repr__(self):
        return '<DictionaryTag>'


class ScalarTag(BaseTag):

    def __init__(self, value, manifest):
        self._value = value
        BaseTag.__init__(self, manifest)

    @property
    def value(self):
        return self._value

    @classmethod
    def from_yaml_node(cls, manifest, loader, node):
        value = loader.construct_scalar(node)
        return cls(value, manifest)


class LazyTag(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def lazy_value(self):
        pass


class LazyScalarTag(ScalarTag, LazyTag):
    __metaclass__ = ABCMeta

    @abstractmethod
    def lazy_value(self):
        pass

