import unittest
from os.path import abspath, join, dirname

from maryjane import Project


class ProjectTestCase(unittest.TestCase):

    def setUp(self):
        self.this_dir = abspath(dirname(__file__))
        self.stuff_dir = join(self.this_dir, 'stuff')
        self.static_dir = join(self.stuff_dir, 'static')

    def test_parser(self):
        project = Project(join(self.stuff_dir, 'maryjane.yaml'))
        root = project.root

        self.assertIsNotNone(root)

        self.assertEqual(root['title'], 'Test Project')
        self.assertEqual(root['version'], '0.1.0')
        self.assertIsNone(root['empty'])

        self.assertEqual(root['static'], join(self.stuff_dir, 'static'))

        self.assertDictEqual(
            root['bag'],
            {
                'avg': .34,
                'count': 1,
                'item1': {
                    'item2': 'value2'
                }
            }
        )

        self.assertEqual(root['task1']['file1'], join(self.stuff_dir, 'static', 'file1.txt'))
        self.assertEqual(root['task1']['files'], [
            join(self.stuff_dir, 'static', 'file1.txt'),
            join(self.stuff_dir, 'static', 'file2.txt'),
        ])

        project.reload()
        root = project.root
        self.assertEqual(root['task1']['file1'], join(self.stuff_dir, 'static', 'file1.txt'))


if __name__ == '__main__':
    unittest.main()
