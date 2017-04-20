# -*- coding: utf-8 -*-

"""Main test script."""

from __future__ import unicode_literals

import os
import unittest

from dependenpy.utils import MatrixBuilder


class AbstractTestCase(unittest.TestCase):
    """Setup and tear down data."""

    def setUp(self):
        """Setup matrix builders with string, list and ordered dict."""
        str_p = 'internal'
        list_p = ['internal']
        od_p = ['Only group', ['internal']]

        self.str_dm = MatrixBuilder(str_p)
        self.list_dm = MatrixBuilder(list_p)
        self.od_dm = MatrixBuilder(od_p)

    def tearDown(self):
        """Delete matrix builders."""
        del self.str_dm
        del self.list_dm
        del self.od_dm


class EmptyTestCase(AbstractTestCase):
    """Test empty matrices."""

    def test_wrong_type(self):
        """Assert AttributeError is raised when given a wrong value."""
        tmp = MatrixBuilder('')
        self.assertRaises(AttributeError, tmp.__init__, 1)

    def test_wrong_list(self):
        """Assert AttributeError is raised when given a wrong list."""
        tmp = MatrixBuilder('')
        self.assertRaises(AttributeError, tmp.__init__, ['', '', ['']])
        self.assertRaises(AttributeError, tmp.__init__, ['', '', [''], ['']])
        self.assertRaises(AttributeError, tmp.__init__, ['', [''], [''], ''])
        self.assertRaises(AttributeError, tmp.__init__, [[''], ''])

    def test_packages(self):
        """Assert packages attribute is correctly set."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(dm.packages, [['internal']])

    def test_groups(self):
        """Assert groups attribute is correctly set."""
        self.assertEqual(self.str_dm.groups, [''])
        self.assertEqual(self.list_dm.groups, [''])
        self.assertEqual(self.od_dm.groups, ['Only group'])

    def test_other_attributes(self):
        """Assert other attributes are correctly set."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(dm.modules, [])
            self.assertEqual(dm.imports, [])
            self.assertEqual(dm.max_depth, 0)
            self.assertEqual(dm.matrices, [])
            self.assertEqual(dm._inside, {})
            self.assertEqual(dm._modules_are_built, False)
            self.assertEqual(dm._imports_are_built, False)
            self.assertEqual(dm._matrices_are_built, False)


class StaticDataTestCase(AbstractTestCase):
    """Test data are never modified again once computed."""

    def test_static(self):
        """Assert build_imports/matrices let modules/imports untouched."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules()
            temp_modules = list(dm.modules)
            self.assertEqual(
                temp_modules,
                dm.build_imports().modules,
                'Modules have been modified by build_imports()')
            temp_imports = list(dm.imports)
            self.assertEqual(
                temp_imports,
                dm.build_matrices().imports,
                'Imports have been modified by build_matrices()')


class NoPathTestCase(unittest.TestCase):
    """Test matrix builder with non-existent package."""

    def setUp(self):
        """Setup matrix builder with unfindable package."""
        self.dm = MatrixBuilder('unfindable')

    def test_modules(self):
        """Assert no module found."""
        self.assertEqual(self.dm.build_modules().modules, [])


class ModuleTestCase(AbstractTestCase):
    """Test building modules methods."""

    def setUp(self):
        """Already build modules."""
        super(ModuleTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules()

    def test_max_depth(self):
        """Assert max depth corresponds."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(dm.max_depth, 4)

    def assertEqualModules(self, modules, group, local_path):
        """Helper to compare modules."""
        self.assertEqual(
            modules,
            [{'group': {'index': 0, 'name': group},
              'name': 'internal.__init__',
              'path': local_path + '/internal/__init__.py'},
             {'group': {'index': 0, 'name': group},
              'name': 'internal.submodule1.__init__',
              'path': local_path + '/internal/submodule1/__init__.py'},
             {'group': {'index': 0, 'name': group},
              'name': 'internal.submodule1.submoduleA.__init__',
              'path': local_path + '/internal/submodule1/submoduleA/__init__.py'},
             # noqa
             {'group': {'index': 0, 'name': group},
              'name': 'internal.submodule1.submoduleA.test',
              'path': local_path + '/internal/submodule1/submoduleA/test.py'},
             {'group': {'index': 0, 'name': group},
              'name': 'internal.submodule1.test',
              'path': local_path + '/internal/submodule1/test.py'},
             {'group': {'index': 0, 'name': group},
              'name': 'internal.submodule2.__init__',
              'path': local_path + '/internal/submodule2/__init__.py'},
             {'group': {'index': 0, 'name': group},
              'name': 'internal.submodule2.test',
              'path': local_path + '/internal/submodule2/test.py'},
             {'group': {'index': 0, 'name': group},
              'name': 'internal.submodule2.test2',
              'path': local_path + '/internal/submodule2/test2.py'},
             {'group': {'index': 0, 'name': group},
              'name': 'internal.test',
              'path': local_path + '/internal/test.py'}])

    def test_modules(self):
        """Test modules."""
        local_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'tests'))
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertTrue(dm.build_modules()._modules_are_built)
            self.assertTrue(dm._modules_are_built)
            self.assertFalse(dm._imports_are_built)
            self.assertFalse(dm._matrices_are_built)
        for dm in [self.str_dm, self.list_dm]:
            self.assertEqualModules(dm.modules, '', local_path)
        self.assertEqualModules(self.od_dm.modules, 'Only group', local_path)


class ImportsTestCase(AbstractTestCase):
    """Test building imports methods."""

    def setUp(self):
        """Already build imports."""
        super(ImportsTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules().build_imports()

    def test_imports(self):
        """Check imports values."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertTrue(dm._modules_are_built)
            self.assertTrue(dm._imports_are_built)
            self.assertFalse(dm._matrices_are_built)
            self.assertEqual(
                dm.imports,
                [{u'cardinal': 9,
                  u'imports': [{u'by': u'internal.submodule1.submoduleA.test',
                                u'from': u'internal.test',
                                u'import': ['someclass',
                                            'classA',
                                            'classB',
                                            'classC',
                                            'classD',
                                            'classE',
                                            'classF',
                                            'classG',
                                            'classH']}],
                  u'source_index': 3,
                  u'source_name': u'internal.submodule1.submoduleA.test',
                  u'target_index': 8,
                  u'target_name': u'internal.test'},
                 {u'cardinal': 2,
                  u'imports': [{u'by': u'internal.submodule1.test',
                                u'from': u'internal.submodule1.submoduleA',
                                u'import': ['test', 'othertest']}],
                  u'source_index': 4,
                  u'source_name': u'internal.submodule1.test',
                  u'target_index': 2,
                  u'target_name': u'internal.submodule1.submoduleA.__init__'},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.submodule1.test',
                                u'from': u'internal.submodule1.submoduleA.test',
                                # noqa
                                u'import': ['Test1']}],
                  u'source_index': 4,
                  u'source_name': u'internal.submodule1.test',
                  u'target_index': 3,
                  u'target_name': u'internal.submodule1.submoduleA.test'},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.submodule1.test',
                                u'from': u'internal',
                                u'import': ['test']}],
                  u'source_index': 4,
                  u'source_name': u'internal.submodule1.test',
                  u'target_index': 0,
                  u'target_name': u'internal.__init__'},
                 {u'cardinal': 1, u'target_index': 5,
                  u'target_name': u'internal.submodule2.__init__', u'source_index': 4,
                  u'source_name': u'internal.submodule1.test', u'imports': [
                     {u'from': u'internal.submodule2', u'import': ['test'],
                      u'by': u'internal.submodule1.test'}]},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.submodule2.test',
                                u'from': u'internal.submodule2.test2',
                                u'import': ['someclass']}],
                  u'source_index': 6,
                  u'source_name': u'internal.submodule2.test',
                  u'target_index': 7,
                  u'target_name': u'internal.submodule2.test2'},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.submodule2.test',
                                u'from': 'internal.submodule1.submoduleA',
                                u'import': ['othertest']}],
                  u'source_index': 6,
                  u'source_name': u'internal.submodule2.test',
                  u'target_index': 2,
                  u'target_name': u'internal.submodule1.submoduleA.__init__'},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.test',
                                u'from': 'internal',
                                u'import': ['submodule2']}],
                  u'source_index': 8,
                  u'source_name': u'internal.test',
                  u'target_index': 0,
                  u'target_name': u'internal.__init__'},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.test',
                                u'from': 'internal.submodule1',
                                u'import': ['submoduleA']}],
                  u'source_index': 8,
                  u'source_name': u'internal.test',
                  u'target_index': 1,
                  u'target_name': u'internal.submodule1.__init__'},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.test',
                                u'from': 'internal.submodule1.submoduleA',
                                u'import': ['test']}],
                  u'source_index': 8,
                  u'source_name': u'internal.test',
                  u'target_index': 2,
                  u'target_name': u'internal.submodule1.submoduleA.__init__'},
                 {u'cardinal': 1,
                  u'imports': [{u'by': u'internal.test',
                                u'from': 'internal.submodule2',
                                u'import': ['doesnotexists']}],
                  u'source_index': 8,
                  u'source_name': u'internal.test',
                  u'target_index': 5,
                  u'target_name': u'internal.submodule2.__init__'}])

    def test_inside(self):
        """Test memorized values."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(dm._inside, {
                'internal.test': True,
                'external.exists': False,
                'internal.submodule2.test2': True,
                'internal.submodule1.submoduleA': True,
                'internal.submodule2': True,
                'internal.submodule1.submoduleA.test': True,
                'internal.submodule1': True,
                'internal': True
            })


class MatricesTestCase(AbstractTestCase):
    """Test building matrices methods."""

    def setUp(self):
        """Already build everything."""
        super(MatricesTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build()

    def test_matrix_to_csv(self):
        """Test CSV output method."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(
                dm.get_matrix(1).to_csv(),
                ',internal\r\n'
                'internal,20',
                'CSV MATRIX 1')
            self.assertEqual(
                dm.get_matrix(2).to_csv(),
                ',internal.__init__,internal.submodule1,'
                'internal.submodule2,internal.test\r\n'
                'internal.__init__,0,0,0,0\r\n'
                'internal.submodule1,1,3,1,9\r\n'
                'internal.submodule2,0,1,1,0\r\n'
                'internal.test,1,2,1,0',
                'CSV MATRIX 2')
            self.assertEqual(
                dm.get_matrix(3).to_csv(),
                u',internal.__init__,internal.submodule1.__init__,'
                u'internal.submodule1.submoduleA,internal.submodule1.test,'
                u'internal.submodule2.__init__,internal.submodule2.test,'
                u'internal.submodule2.test2,internal.test\r\n'
                u'internal.__init__,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule1.__init__,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule1.submoduleA,0,0,0,0,0,0,0,9\r\n'
                u'internal.submodule1.test,1,0,3,0,1,0,0,0\r\n'
                u'internal.submodule2.__init__,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule2.test,0,0,1,0,0,0,1,0\r\n'
                u'internal.submodule2.test2,0,0,0,0,0,0,0,0\r\n'
                u'internal.test,1,1,1,0,1,0,0,0',
                'CSV MATRIX 3')
            self.assertEqual(
                dm.get_matrix(4).to_csv(),
                u',internal.__init__,internal.submodule1.__init__,'
                u'internal.submodule1.submoduleA.__init__,'
                u'internal.submodule1.submoduleA.test,'
                u'internal.submodule1.test,'
                u'internal.submodule2.__init__,internal.submodule2.test,'
                u'internal.submodule2.test2,internal.test\r\n'
                u'internal.__init__,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule1.__init__,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule1.submoduleA.__init__,0,0,0,0,0,0,0,0,0\r\n'  # noqa
                u'internal.submodule1.submoduleA.test,0,0,0,0,0,0,0,0,9\r\n'
                u'internal.submodule1.test,1,0,2,1,0,1,0,0,0\r\n'
                u'internal.submodule2.__init__,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule2.test,0,0,1,0,0,0,0,1,0\r\n'
                u'internal.submodule2.test2,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.test,1,1,1,0,0,1,0,0,0',
                'CSV MATRIX 4')


class OrderTestCase(AbstractTestCase):
    """Test order of method execution."""

    def test_wrong_order(self):
        """Test order of method execution."""
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


class SortingTestCase(AbstractTestCase):
    """Test sorting methods."""

    def test_order_computing(self):
        """Test the method calculating all orders at once."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build()
            for m in dm.matrices:
                m.compute_orders()

    def test_sort_method(self):
        """Test sort method with each possible order."""
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build()
            for m in dm.matrices:
                for s in m.orders.keys():
                    m.sort(s)
                    m.sort(s, reverse=True)

