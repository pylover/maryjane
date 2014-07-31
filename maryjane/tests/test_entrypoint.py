__author__ = 'vahid'

import unittest
import os
import time
from maryjane import main
import hashlib
from datetime import datetime

class EntrypointTester(unittest.TestCase):

    def setUp(self):
        self.this_dir = os.path.dirname(__file__)
        self.manifest_file = os.path.join(self.this_dir, 'maryjane.yaml')
        self.out_files = [os.path.join(self.this_dir, 'stuff', f) for f in ('a-b.txt', 'a-b.tar.gz')]
        self.input_files = [os.path.join(self.this_dir, 'stuff', f) for f in ('a.txt', 'b.txt')]

    def cleanup(self):
        for f in self.out_files:
            if os.path.exists(f):
                os.remove(f)

    def test_main(self):
        self.cleanup()
        main(self.manifest_file)

        for f in self.out_files:
            self.assertTrue(os.path.exists(f))

    @staticmethod
    def md5(filename, block_size=2048):
        md5 = hashlib.md5()

        with open(filename) as f:
            block = f.read(block_size)
            while block:
                md5.update(block)
                block = f.read(block_size)
        return md5.hexdigest()


    def test_watch(self):
        self.cleanup()
        main(self.manifest_file, enable_watcher=True)

        for f in self.out_files:
            self.assertTrue(os.path.exists(f))

        files_checksum = [self.md5(f) for f in self.out_files]

        # Trying to change an input file
        with open(self.input_files[0], 'w') as input_file:
            input_file.write("This file recently changed at: %s" % datetime.now().strftime('%Y-%m-%d %H:%M'))
            input_file.flush()

        with open(self.input_files[0], 'a') as input_file:
            input_file.write("This file recently changed at: %s" % datetime.now().strftime('%Y-%m-%d %H:%M'))
            input_file.flush()

        time.sleep(5)

        new_files_checksum = [self.md5(f) for f in self.out_files]

        for i in range(len(self.out_files)):
            self.assertNotEqual(files_checksum[i], new_files_checksum[i])



if __name__ == '__main__':
    unittest.main()
