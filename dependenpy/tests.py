import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import unittest
from collections import OrderedDict
from dependenpy.utils import DependencyMatrix


class AbstractTestCase(unittest.TestCase):

    def setUp(self):

        str_p = 'internal'
        list_p = ['internal']
        od_p = OrderedDict()
        od_p['Only group'] = ['internal']

        self.str_dm = DependencyMatrix(str_p)
        self.list_dm = DependencyMatrix(list_p)
        self.od_dm = DependencyMatrix(od_p)

    def tearDown(self):
        del self.str_dm
        del self.list_dm
        del self.od_dm


class EmptyTestCase(AbstractTestCase):

    def test_wrong_type(self):
        tmp = DependencyMatrix('')
        self.assertRaises(AttributeError, tmp.__init__, 1)

    def test_packages(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
                self.assertEqual(dm.packages, [['internal']])

    def test_groups(self):
        self.assertEqual(self.str_dm.groups, [''])
        self.assertEqual(self.list_dm.groups, [''])
        self.assertEqual(self.od_dm.groups, ['Only group'])

    def test_other_attributes(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(dm.modules, [])
            self.assertEqual(dm.imports, [])
            self.assertEqual(dm.max_depth, 0)
            self.assertEqual(dm.matrices, [])
            self.assertEqual(dm._inside, {})
            self.assertEqual(dm._modules_are_built, False)
            self.assertEqual(dm._imports_are_built, False)
            self.assertEqual(dm._matrices_are_built, False)


class ModuleTestCase(AbstractTestCase):

    def setUp(self):
        super(ModuleTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules()

    def test_max_depth(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertTrue(dm._modules_are_built)
            self.assertEqual(dm.max_depth, 4)

    def test_modules(self):
        local_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'tests'))
        for dm in [self.str_dm, self.list_dm]:
            self.assertEqual(dm.modules, [
                {
                    'path': local_path+'/internal/submodule1/submoduleA/__init__.py',
                    'group_index': 0,
                    'name': 'internal.submodule1.submoduleA.__init__',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/submodule1/submoduleA/test.py',
                    'group_index': 0,
                    'name': 'internal.submodule1.submoduleA.test',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/submodule1/__init__.py',
                    'group_index': 0,
                    'name': 'internal.submodule1.__init__',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/submodule1/test.py',
                    'group_index': 0,
                    'name': 'internal.submodule1.test',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/submodule2/__init__.py',
                    'group_index': 0,
                    'name': 'internal.submodule2.__init__',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/submodule2/test.py',
                    'group_index': 0,
                    'name': 'internal.submodule2.test',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/submodule2/test2.py',
                    'group_index': 0,
                    'name': 'internal.submodule2.test2',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/__init__.py',
                    'group_index': 0,
                    'name': 'internal.__init__',
                    'group_name': ''
                },
                {
                    'path': local_path+'/internal/test.py',
                    'group_index': 0,
                    'name': 'internal.test',
                    'group_name': ''
                }
            ])
        self.assertEqual(self.od_dm.modules, [
            {
                'path': local_path+'/internal/submodule1/submoduleA/__init__.py',
                'group_index': 0,
                'name': 'internal.submodule1.submoduleA.__init__',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/submodule1/submoduleA/test.py',
                'group_index': 0,
                'name': 'internal.submodule1.submoduleA.test',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/submodule1/__init__.py',
                'group_index': 0,
                'name': 'internal.submodule1.__init__',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/submodule1/test.py',
                'group_index': 0,
                'name': 'internal.submodule1.test',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/submodule2/__init__.py',
                'group_index': 0,
                'name': 'internal.submodule2.__init__',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/submodule2/test.py',
                'group_index': 0,
                'name': 'internal.submodule2.test',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/submodule2/test2.py',
                'group_index': 0,
                'name': 'internal.submodule2.test2',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/__init__.py',
                'group_index': 0,
                'name': 'internal.__init__',
                'group_name': 'Only group'
            },
            {
                'path': local_path+'/internal/test.py',
                'group_index': 0,
                'name': 'internal.test',
                'group_name': 'Only group'
            }
        ])


class ImportsTestCase(AbstractTestCase):

    def setUp(self):
        super(ImportsTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules().build_imports()

    def test_imports(self):
        pass


class MatricesTestCase(AbstractTestCase):

    def setUp(self):
        super(MatricesTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules().build_imports().build_matrices()

    def test_matrices(self):
        pass


class WrongOrderTestCase(AbstractTestCase):

    def test_wrong_order(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_matrices()
            self.assertFalse(dm._matrices_are_built)
            self.assertFalse(dm._imports_are_built)
            self.assertFalse(dm._modules_are_built)

            dm.build_imports()
            self.assertFalse(dm._matrices_are_built)
            self.assertFalse(dm._imports_are_built)
            self.assertFalse(dm._modules_are_built)

            dm.build_matrices()
            self.assertFalse(dm._matrices_are_built)
            self.assertFalse(dm._imports_are_built)
            self.assertFalse(dm._modules_are_built)

            dm.build_modules()
            self.assertFalse(dm._matrices_are_built)
            self.assertFalse(dm._imports_are_built)
            self.assertTrue(dm._modules_are_built)

            dm.build_matrices()
            self.assertFalse(dm._matrices_are_built)
            self.assertFalse(dm._imports_are_built)
            self.assertTrue(dm._modules_are_built)

            dm.build_imports()
            self.assertFalse(dm._matrices_are_built)
            self.assertTrue(dm._imports_are_built)
            self.assertTrue(dm._modules_are_built)

            dm.build_matrices()
            self.assertTrue(dm._matrices_are_built)
            self.assertTrue(dm._imports_are_built)
            self.assertTrue(dm._modules_are_built)


if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'tests')))
    unittest.main()