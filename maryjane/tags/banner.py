# -*- coding: utf-8 -*-
from __future__ import print_function

from maryjane.tags.action import ActionTag


class BannerActionTag(ActionTag):

    def __init__(self, manifest, **attributes):
        super(BannerActionTag, self).__init__(manifest, **attributes)

    def execute(self):
        super(BannerActionTag, self).execute()
        print(self.text)

    def __repr__(self):
        return '<BannerActionTag %s>' % self.executable

