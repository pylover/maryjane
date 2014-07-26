__author__ = 'vahid'

import unittest
from maryjane import Manifest, main


class EntrypointTester(unittest.TestCase):
    def test_main(self):
        main('maryjane.yaml')


if __name__ == '__main__':
    unittest.main()
