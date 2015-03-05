import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import unittest
import json
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
            self.assertEqual(dm.max_depth, 4)

    def assertEqualModules(self, modules, group, local_path):
        self.assertEqual(modules, [
            {
                'path': local_path + '/internal/submodule1/submoduleA/__init__.py',
                'group_index': 0,
                'name': 'internal.submodule1.submoduleA.__init__',
                'group_name': group
            },
            {
                'path': local_path + '/internal/submodule1/submoduleA/test.py',
                'group_index': 0,
                'name': 'internal.submodule1.submoduleA.test',
                'group_name': group
            },
            {
                'path': local_path + '/internal/submodule1/__init__.py',
                'group_index': 0,
                'name': 'internal.submodule1.__init__',
                'group_name': group
            },
            {
                'path': local_path + '/internal/submodule1/test.py',
                'group_index': 0,
                'name': 'internal.submodule1.test',
                'group_name': group
            },
            {
                'path': local_path + '/internal/submodule2/__init__.py',
                'group_index': 0,
                'name': 'internal.submodule2.__init__',
                'group_name': group
            },
            {
                'path': local_path + '/internal/submodule2/test.py',
                'group_index': 0,
                'name': 'internal.submodule2.test',
                'group_name': group
            },
            {
                'path': local_path + '/internal/submodule2/test2.py',
                'group_index': 0,
                'name': 'internal.submodule2.test2',
                'group_name': group
            },
            {
                'path': local_path + '/internal/__init__.py',
                'group_index': 0,
                'name': 'internal.__init__',
                'group_name': group
            },
            {
                'path': local_path + '/internal/test.py',
                'group_index': 0,
                'name': 'internal.test',
                'group_name': group
            }
        ])

    def test_modules(self):
        local_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'tests'))
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertTrue(dm._modules_are_built)
            self.assertFalse(dm._imports_are_built)
            self.assertFalse(dm._matrices_are_built)
        for dm in [self.str_dm, self.list_dm]:
            self.assertEqualModules(dm.modules, '', local_path)
        self.assertEqualModules(self.od_dm.modules, 'Only group', local_path)


class ImportsTestCase(AbstractTestCase):
    def setUp(self):
        super(ImportsTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules()
            dm.build_imports()

    def test_imports(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertTrue(dm._modules_are_built)
            self.assertTrue(dm._imports_are_built)
            self.assertFalse(dm._matrices_are_built)
            self.assertEqual(
                dm.imports,
                [ { 'cardinal': 9,
                    'imports': [ { 'by': 'internal.submodule1.submoduleA.test',
                                   'from': 'internal.test',
                                   'import': [ 'someclass',
                                               'classA',
                                               'classB',
                                               'classC',
                                               'classD',
                                               'classE',
                                               'classF',
                                               'classG',
                                               'classH']}],
                    'source_index': 1,
                    'source_name': 'internal.submodule1.submoduleA.test',
                    'target_index': 8,
                    'target_name': 'internal.test'},
                  { 'cardinal': 2,
                    'imports': [ { 'by': 'internal.submodule1.test',
                                   'from': 'internal.submodule1.submoduleA',
                                   'import': ['test', 'othertest']}],
                    'source_index': 3,
                    'source_name': 'internal.submodule1.test',
                    'target_index': 0,
                    'target_name': 'internal.submodule1.submoduleA.__init__'},
                  { 'cardinal': 1,
                    'imports': [ { 'by': 'internal.submodule1.test',
                                   'from': 'internal.submodule1.submoduleA.test',
                                   'import': ['Test1']}],
                    'source_index': 3,
                    'source_name': 'internal.submodule1.test',
                    'target_index': 1,
                    'target_name': 'internal.submodule1.submoduleA.test'},
                  { 'cardinal': 1,
                    'imports': [ { 'by': 'internal.submodule1.test',
                                   'from': 'internal',
                                   'import': ['test']}],
                    'source_index': 3,
                    'source_name': 'internal.submodule1.test',
                    'target_index': 7,
                    'target_name': 'internal.__init__'},
                  { 'cardinal': 1,
                    'imports': [ { 'by': 'internal.submodule2.test',
                                   'from': 'internal.submodule2.test2',
                                   'import': ['someclass']}],
                    'source_index': 5,
                    'source_name': 'internal.submodule2.test',
                    'target_index': 6,
                    'target_name': 'internal.submodule2.test2'},
                  { 'cardinal': 1,
                    'imports': [ { 'by': 'internal.test',
                                   'from': 'internal',
                                   'import': ['submodule2']}],
                    'source_index': 8,
                    'source_name': 'internal.test',
                    'target_index': 7,
                    'target_name': 'internal.__init__'},
                  { 'cardinal': 1,
                    'imports': [ { 'by': 'internal.test',
                                   'from': 'internal.submodule1',
                                   'import': ['submoduleA']}],
                    'source_index': 8,
                    'source_name': 'internal.test',
                    'target_index': 2,
                    'target_name': 'internal.submodule1.__init__'},
                  { 'cardinal': 1,
                    'imports': [ { 'by': 'internal.test',
                                   'from': 'internal.submodule1.submoduleA',
                                   'import': ['test']}],
                    'source_index': 8,
                    'source_name': 'internal.test',
                    'target_index': 0,
                    'target_name': 'internal.submodule1.submoduleA.__init__'},
                  { 'cardinal': 1,
                    'imports': [ { 'by': 'internal.test',
                                   'from': 'internal.submodule2',
                                   'import': ['doesnotexists']}],
                    'source_index': 8,
                    'source_name': 'internal.test',
                    'target_index': 4,
                    'target_name': 'internal.submodule2.__init__'}])

    def test_inside(self):
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

    def setUp(self):
        super(MatricesTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules().build_imports().build_matrices()

    def assertEqualMatrices(self, dm, group, local_path):
        self.assertEqual(
            dm.get_matrix(1),
            { 'imports': [ { 'cardinal': 18,
                             'imports': [ { 'by': 'internal.submodule1.submoduleA.test',
                                            'from': 'internal.test',
                                            'import': [ 'someclass',
                                                        'classA',
                                                        'classB',
                                                        'classC',
                                                        'classD',
                                                        'classE',
                                                        'classF',
                                                        'classG',
                                                        'classH']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test', 'othertest']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal',
                                            'import': ['test']},
                                          { 'by': 'internal.submodule2.test',
                                            'from': 'internal.submodule2.test2',
                                            'import': ['someclass']},
                                          { 'by': 'internal.test',
                                            'from': 'internal',
                                            'import': ['submodule2']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1',
                                            'import': ['submoduleA']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule2',
                                            'import': ['doesnotexists']}],
                             'source_index': 0,
                             'source_name': 'internal',
                             'target_index': 0,
                             'target_name': 'internal'}],
              'modules': [{ 'group_index': 0, 'group_name': group, 'name': 'internal'}]},
            'Depth 1 not equal')
        self.assertEqual(
            dm.get_matrix(2),
            { 'imports': [ { 'cardinal': 9,
                             'imports': [ { 'by': 'internal.submodule1.submoduleA.test',
                                            'from': 'internal.test',
                                            'import': [ 'someclass',
                                                        'classA',
                                                        'classB',
                                                        'classC',
                                                        'classD',
                                                        'classE',
                                                        'classF',
                                                        'classG',
                                                        'classH']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test', 'othertest']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal',
                                            'import': ['test']},
                                          { 'by': 'internal.submodule2.test',
                                            'from': 'internal.submodule2.test2',
                                            'import': ['someclass']},
                                          { 'by': 'internal.test',
                                            'from': 'internal',
                                            'import': ['submodule2']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1',
                                            'import': ['submoduleA']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule2',
                                            'import': ['doesnotexists']}],
                             'source_index': 0,
                             'source_name': 'internal.submodule1',
                             'target_index': 3,
                             'target_name': 'internal.test'},
                           { 'cardinal': 3,
                             'imports': [ { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test', 'othertest']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']}],
                             'source_index': 0,
                             'source_name': 'internal.submodule1',
                             'target_index': 0,
                             'target_name': 'internal.submodule1'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.submodule1.test',
                                            'from': 'internal',
                                            'import': ['test']}],
                             'source_index': 0,
                             'source_name': 'internal.submodule1',
                             'target_index': 2,
                             'target_name': 'internal.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.submodule2.test',
                                            'from': 'internal.submodule2.test2',
                                            'import': ['someclass']}],
                             'source_index': 1,
                             'source_name': 'internal.submodule2',
                             'target_index': 1,
                             'target_name': 'internal.submodule2'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal',
                                            'import': ['submodule2']}],
                             'source_index': 3,
                             'source_name': 'internal.test',
                             'target_index': 2,
                             'target_name': 'internal.__init__'},
                           { 'cardinal': 2,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule1',
                                            'import': ['submoduleA']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']}],
                             'source_index': 3,
                             'source_name': 'internal.test',
                             'target_index': 0,
                             'target_name': 'internal.submodule1'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule2',
                                            'import': ['doesnotexists']}],
                             'source_index': 3,
                             'source_name': 'internal.test',
                             'target_index': 1,
                             'target_name': 'internal.submodule2'}],
              'modules': [ { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule2'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.__init__'},
                           { 'group_index': 0, 'group_name': group, 'name': 'internal.test'}]},
            'Depth 2 not equal')
        self.assertEqual(
            dm.get_matrix(3),
            { 'imports': [ { 'cardinal': 9,
                             'imports': [ { 'by': 'internal.submodule1.submoduleA.test',
                                            'from': 'internal.test',
                                            'import': [ 'someclass',
                                                        'classA',
                                                        'classB',
                                                        'classC',
                                                        'classD',
                                                        'classE',
                                                        'classF',
                                                        'classG',
                                                        'classH']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test', 'othertest']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal',
                                            'import': ['test']},
                                          { 'by': 'internal.submodule2.test',
                                            'from': 'internal.submodule2.test2',
                                            'import': ['someclass']},
                                          { 'by': 'internal.test',
                                            'from': 'internal',
                                            'import': ['submodule2']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1',
                                            'import': ['submoduleA']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule2',
                                            'import': ['doesnotexists']}],
                             'source_index': 0,
                             'source_name': 'internal.submodule1.submoduleA',
                             'target_index': 7,
                             'target_name': 'internal.test'},
                           { 'cardinal': 3,
                             'imports': [ { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test', 'othertest']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']}],
                             'source_index': 2,
                             'source_name': 'internal.submodule1.test',
                             'target_index': 0,
                             'target_name': 'internal.submodule1.submoduleA'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.submodule1.test',
                                            'from': 'internal',
                                            'import': ['test']}],
                             'source_index': 2,
                             'source_name': 'internal.submodule1.test',
                             'target_index': 6,
                             'target_name': 'internal.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.submodule2.test',
                                            'from': 'internal.submodule2.test2',
                                            'import': ['someclass']}],
                             'source_index': 4,
                             'source_name': 'internal.submodule2.test',
                             'target_index': 5,
                             'target_name': 'internal.submodule2.test2'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal',
                                            'import': ['submodule2']}],
                             'source_index': 7,
                             'source_name': 'internal.test',
                             'target_index': 6,
                             'target_name': 'internal.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule1',
                                            'import': ['submoduleA']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']}],
                             'source_index': 7,
                             'source_name': 'internal.test',
                             'target_index': 1,
                             'target_name': 'internal.submodule1.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']}],
                             'source_index': 7,
                             'source_name': 'internal.test',
                             'target_index': 0,
                             'target_name': 'internal.submodule1.submoduleA'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule2',
                                            'import': ['doesnotexists']}],
                             'source_index': 7,
                             'source_name': 'internal.test',
                             'target_index': 3,
                             'target_name': 'internal.submodule2.__init__'}],
              'modules': [ { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1.submoduleA'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1.__init__'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1.test'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule2.__init__'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule2.test'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule2.test2'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.__init__'},
                           { 'group_index': 0, 'group_name': group, 'name': 'internal.test'}]},
            'Depth 3 not equal')
        self.assertEqual(
            dm.get_matrix(4),
            { 'imports': [ { 'cardinal': 9,
                             'imports': [ { 'by': 'internal.submodule1.submoduleA.test',
                                            'from': 'internal.test',
                                            'import': [ 'someclass',
                                                        'classA',
                                                        'classB',
                                                        'classC',
                                                        'classD',
                                                        'classE',
                                                        'classF',
                                                        'classG',
                                                        'classH']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test', 'othertest']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal',
                                            'import': ['test']},
                                          { 'by': 'internal.submodule2.test',
                                            'from': 'internal.submodule2.test2',
                                            'import': ['someclass']},
                                          { 'by': 'internal.test',
                                            'from': 'internal',
                                            'import': ['submodule2']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1',
                                            'import': ['submoduleA']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule2',
                                            'import': ['doesnotexists']}],
                             'source_index': 1,
                             'source_name': 'internal.submodule1.submoduleA.test',
                             'target_index': 8,
                             'target_name': 'internal.test'},
                           { 'cardinal': 2,
                             'imports': [ { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test', 'othertest']},
                                          { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']}],
                             'source_index': 3,
                             'source_name': 'internal.submodule1.test',
                             'target_index': 0,
                             'target_name': 'internal.submodule1.submoduleA.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.submodule1.test',
                                            'from': 'internal.submodule1.submoduleA.test',
                                            'import': ['Test1']}],
                             'source_index': 3,
                             'source_name': 'internal.submodule1.test',
                             'target_index': 1,
                             'target_name': 'internal.submodule1.submoduleA.test'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.submodule1.test',
                                            'from': 'internal',
                                            'import': ['test']}],
                             'source_index': 3,
                             'source_name': 'internal.submodule1.test',
                             'target_index': 7,
                             'target_name': 'internal.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.submodule2.test',
                                            'from': 'internal.submodule2.test2',
                                            'import': ['someclass']}],
                             'source_index': 5,
                             'source_name': 'internal.submodule2.test',
                             'target_index': 6,
                             'target_name': 'internal.submodule2.test2'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal',
                                            'import': ['submodule2']}],
                             'source_index': 8,
                             'source_name': 'internal.test',
                             'target_index': 7,
                             'target_name': 'internal.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule1',
                                            'import': ['submoduleA']},
                                          { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']}],
                             'source_index': 8,
                             'source_name': 'internal.test',
                             'target_index': 2,
                             'target_name': 'internal.submodule1.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule1.submoduleA',
                                            'import': ['test']}],
                             'source_index': 8,
                             'source_name': 'internal.test',
                             'target_index': 0,
                             'target_name': 'internal.submodule1.submoduleA.__init__'},
                           { 'cardinal': 1,
                             'imports': [ { 'by': 'internal.test',
                                            'from': 'internal.submodule2',
                                            'import': ['doesnotexists']}],
                             'source_index': 8,
                             'source_name': 'internal.test',
                             'target_index': 4,
                             'target_name': 'internal.submodule2.__init__'}],
              'modules': [ { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1.submoduleA.__init__',
                             'path': local_path + '/internal/submodule1/submoduleA/__init__.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1.submoduleA.test',
                             'path': local_path + '/internal/submodule1/submoduleA/test.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1.__init__',
                             'path': local_path + '/internal/submodule1/__init__.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule1.test',
                             'path': local_path + '/internal/submodule1/test.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule2.__init__',
                             'path': local_path + '/internal/submodule2/__init__.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule2.test',
                             'path': local_path + '/internal/submodule2/test.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.submodule2.test2',
                             'path': local_path + '/internal/submodule2/test2.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.__init__',
                             'path': local_path + '/internal/__init__.py'},
                           { 'group_index': 0,
                             'group_name': group,
                             'name': 'internal.test',
                             'path': local_path + '/internal/test.py'}]},
            'Depth 4 not equal')

    def test_matrices(self):
        local_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'tests'))
        for dm in [self.str_dm, self.list_dm]:
            self.assertEqualMatrices(dm, '', local_path)
        self.assertEqualMatrices(self.od_dm, 'Only group', local_path)
        for dm in [self.str_dm, self.list_dm]:
            self.assertEqual(dm.get_matrix(0), dm.get_matrix(dm.max_depth))
            self.assertEqual(dm.get_matrix(dm.max_depth), dm.get_matrix(dm.max_depth+1))
            self.assertEqual(dm.get_matrix(1), dm.get_matrix(-1))

            for i in range(1, dm.max_depth-1):
                self.assertNotEqual(dm.get_matrix(i), dm.get_matrix(i+1))


class JSONTestCase(AbstractTestCase):

    def setUp(self):
        super(JSONTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build()

    def test_load_json_dump(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            data = json.loads(dm.to_json())

            obj = DependencyMatrix(data['packages'])
            obj.groups = data['groups']
            obj.modules = data['modules']
            obj.imports = data['imports']
            obj.matrices = data['matrices']
            obj.max_depth = data['max_depth']
            obj._inside = data['_inside']
            obj._modules_are_built = data['_modules_are_built']
            obj._imports_are_built = data['_imports_are_built']
            obj._matrices_are_built = data['_matrices_are_built']
            self.assertEqual(dm, obj, 'JSON dump/load/assign')

            obj2 = DependencyMatrix(data['packages'])
            obj2.groups = data['groups']
            obj2.build()
            self.assertEqual(dm, obj2, 'JSON dump/load/build')

    def test_matrix_to_json(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            for i in range(1, dm.max_depth):
                self.assertEqual(
                    dm.get_matrix(i),
                    json.loads(dm.matrix_to_json(i)),
                    'JSON MATRIX dump/load %s' % i
                )

    def test_matrix_to_csv(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(dm.matrix_to_csv(1),
                             ',internal\r\n'
                             'internal,18',
                             'CSV MATRIX 1')
            self.assertEqual(dm.matrix_to_csv(2),
                             ',internal.submodule1,internal.submodule2,internal.__init__,internal.test\r\n'
                             'internal.submodule1,3,0,1,9\r\n'
                             'internal.submodule2,0,1,0,0\r\n'
                             'internal.__init__,0,0,0,0\r\n'
                             'internal.test,2,1,1,0',
                             'CSV MATRIX 2')
            self.assertEqual(dm.matrix_to_csv(3),
                             ',internal.submodule1.submoduleA,internal.submodule1.__init__,internal.submodule1.test,internal.submodule2.__init__,internal.submodule2.test,internal.submodule2.test2,internal.__init__,internal.test\r\n'
                             'internal.submodule1.submoduleA,0,0,0,0,0,0,0,9\r\n'
                             'internal.submodule1.__init__,0,0,0,0,0,0,0,0\r\n'
                             'internal.submodule1.test,3,0,0,0,0,0,1,0\r\n'
                             'internal.submodule2.__init__,0,0,0,0,0,0,0,0\r\n'
                             'internal.submodule2.test,0,0,0,0,0,1,0,0\r\n'
                             'internal.submodule2.test2,0,0,0,0,0,0,0,0\r\n'
                             'internal.__init__,0,0,0,0,0,0,0,0\r\n'
                             'internal.test,1,1,0,1,0,0,1,0',
                             'CSV MATRIX 3')
            self.assertEqual(dm.matrix_to_csv(4),
                             ',internal.submodule1.submoduleA.__init__,internal.submodule1.submoduleA.test,internal.submodule1.__init__,internal.submodule1.test,internal.submodule2.__init__,internal.submodule2.test,internal.submodule2.test2,internal.__init__,internal.test\r\n'
                             'internal.submodule1.submoduleA.__init__,0,0,0,0,0,0,0,0,0\r\n'
                             'internal.submodule1.submoduleA.test,0,0,0,0,0,0,0,0,9\r\n'
                             'internal.submodule1.__init__,0,0,0,0,0,0,0,0,0\r\n'
                             'internal.submodule1.test,2,1,0,0,0,0,0,1,0\r\n'
                             'internal.submodule2.__init__,0,0,0,0,0,0,0,0,0\r\n'
                             'internal.submodule2.test,0,0,0,0,0,0,1,0,0\r\n'
                             'internal.submodule2.test2,0,0,0,0,0,0,0,0,0\r\n'
                             'internal.__init__,0,0,0,0,0,0,0,0,0\r\n'
                             'internal.test,1,0,1,0,1,0,0,1,0',
                             'CSV MATRIX 4')


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