__author__ = 'vahid'

import unittest
import os
from maryjane import Manifest, main


class EntrypointTester(unittest.TestCase):
    def test_main(self):
        this_dir = os.path.dirname(__file__)
        out_files = [os.path.join(this_dir, 'stuff', f) for f in ('a-b.txt', 'a-b.tar.gz')]
        for f in out_files:
            if os.path.exists(f):
                os.remove(f)

        main('maryjane.yaml')

        for f in out_files:
            self.assertTrue(os.path.exists(f))


if __name__ == '__main__':
    unittest.main()
