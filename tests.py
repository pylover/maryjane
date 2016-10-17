import unittest
import time
import random
from subprocess import CalledProcessError
from os.path import abspath, join, dirname

from maryjane import Project, Observer, MaryjaneSyntaxError

WAIT = 1


class ProjectTestCase(unittest.TestCase):

    def setUp(self):
        self.this_dir = abspath(dirname(__file__))
        self.stuff_dir = join(self.this_dir, 'test_stuff')
        self.static_dir = join(self.stuff_dir, 'static')
        self.contrib_dir = join(self.stuff_dir, 'contrib')
        self.temp_dir = join(self.stuff_dir, '../temp')

    def test_parser(self):
        project = Project(join(self.stuff_dir, 'maryjane.yml'), watcher_type=None)
        root = project.root

        self.assertIsNotNone(root)

        self.assertEqual(root['title'], '''
A simple multi-line
text.A simple multi-line
# not commented
text. ''')
        self.assertEqual(root['version'], '0.1.0')
        self.assertIsNone(root['empty'])

        self.assertEqual(root['static'], join(self.stuff_dir, 'static'))

        self.assertDictEqual(
            root['bag'],
            {
                'avg': .34,
                'count': 11,
                'item1': {
                    'item2': 'value2'
                }
            }
        )

        self.assertEqual(root['text_files']['file1'], join(self.stuff_dir, 'static', 'file1.txt'))
        self.assertEqual(root['text_files']['files'], [
            join(self.stuff_dir, 'static', 'file2.txt'),
            join(self.stuff_dir, 'static', 'file3.txt'),
            join(self.stuff_dir, 'contrib', 'file1.txt'),
            join(self.stuff_dir, 'static', 'misc', 'no-watch-file.txt'),
            join(self.stuff_dir, 'static', 'misc', 'file1.txt'),
        ])

        self.assertRaises(AttributeError, lambda: root.non_exists)

        project.reload()
        root = project.root
        self.assertEqual(root['text_files']['file1'], join(self.stuff_dir, 'static', 'file1.txt'))

    def test_watch(self):
        file1 = join(self.static_dir, 'file1.txt')
        misc_file1 = join(self.static_dir, 'misc', 'file1.txt')
        nowatch_file1 = join(self.static_dir, 'misc', 'no-watch-file.txt')
        unused_file = join(self.contrib_dir, 'unused-file.txt')
        dummy_file = join(self.contrib_dir, 'dummy-file.txt')
        outfile = join(self.temp_dir, 'out.txt')

        # Reset files
        with open(file1, 'w') as f:
            f.write('file1\n')

        with open(misc_file1, 'w') as f:
            f.write('misc file1\n')

        with open(nowatch_file1, 'w') as f:
            f.write('excluded file\n')

        project = Project(join(self.stuff_dir, 'maryjane.yml'), watcher_type=Observer)
        project.watcher.start()
        time.sleep(WAIT)

        # Simple watch
        with open(file1, 'w') as f:
            f.write('file1 edited.\n')

        time.sleep(WAIT)
        with open(outfile) as f:
            self.assertEqual(f.readline().strip(), 'file1 edited.')

        with open(file1, 'w') as f:
            f.write('file1\n')

        time.sleep(WAIT)
        with open(outfile) as f:
            self.assertEqual(f.readline().strip(), 'file1')

        # Recursive watch test
        with open(misc_file1, 'w') as f:
            f.write('misc file1 edited.\n')

        time.sleep(WAIT)
        with open(outfile) as f:
            self.assertEqual(next(reversed(f.readlines())).strip(), 'misc file1 edited.')

        with open(misc_file1, 'w') as f:
            f.write('misc file1\n')

        time.sleep(WAIT)
        with open(outfile) as f:
            self.assertEqual(next(reversed(f.readlines())).strip(), 'misc file1')

        # Exclude
        with open(nowatch_file1, 'w') as f:
            f.write('excluded edited file.\n')

        time.sleep(WAIT)
        with open(outfile) as f:
            self.assertNotIn('excluded edited file.', f.read())

        with open(nowatch_file1, 'w') as f:
            f.write('excluded file\n')

        # Single file watch
        with open(unused_file, 'w') as f:
            f.write('Some dummy texts: %s.\n' % random.random())
        time.sleep(WAIT)

        # Watch in root of maryjane.yml
        with open(dummy_file, 'w') as f:
            f.write('Some dummy data: %s.\n' % random.random())
        time.sleep(WAIT)

    def test_exceptions(self):
        self.assertRaises(MaryjaneSyntaxError, Project, join(self.stuff_dir, 'bad-file.yml'))
        self.assertRaises(MaryjaneSyntaxError, Project, join(self.stuff_dir, 'invalid-directive.yml'))
        self.assertRaises(CalledProcessError, Project, join(self.stuff_dir, 'subprocess-error.yml'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
