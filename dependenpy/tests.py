# -*- coding: utf-8 -*-

# Copyright (c) 2015 Timothée Mazzucotelli
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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


class StaticDataTestCase(AbstractTestCase):
    def test_static(self):
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
    def setUp(self):
        self.dm = DependencyMatrix('unfoundable')

    def test_modules(self):
        self.assertEqual(self.dm.build_modules().modules, [])


class ModuleTestCase(AbstractTestCase):
    def setUp(self):
        super(ModuleTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules()

    def test_max_depth(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(dm.max_depth, 4)

    def assertEqualModules(self, modules, group, local_path):
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
    def setUp(self):
        super(ImportsTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules().build_imports()

    def test_imports(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertTrue(dm._modules_are_built)
            self.assertTrue(dm._imports_are_built)
            self.assertFalse(dm._matrices_are_built)
            self.assertEqual(
                dm.imports,
                [{'cardinal': 9,
                  'imports': [{'by': 'internal.submodule1.submoduleA.test',
                               'from': 'internal.test',
                               'import': ['someclass',
                                          'classA',
                                          'classB',
                                          'classC',
                                          'classD',
                                          'classE',
                                          'classF',
                                          'classG',
                                          'classH']}],
                  'source_index': 0,
                  'source_name': 'internal.submodule1.submoduleA.test',
                  'target_index': 8,
                  'target_name': 'internal.test'},
                 {'cardinal': 2,
                  'imports': [{'by': 'internal.submodule1.test',
                               'from': 'internal.submodule1.submoduleA',
                               'import': ['test', 'othertest']}],
                  'source_index': 1,
                  'source_name': 'internal.submodule1.test',
                  'target_index': 2,
                  'target_name': 'internal.submodule1.submoduleA.__init__'},
                 {'cardinal': 1,
                  'imports': [{'by': 'internal.submodule1.test',
                               'from': 'internal.submodule1.submoduleA.test',
                               'import': ['Test1']}],
                  'source_index': 2,
                  'source_name': 'internal.submodule1.test',
                  'target_index': 3,
                  'target_name': 'internal.submodule1.submoduleA.test'},
                 {'cardinal': 1,
                  'imports': [{'by': 'internal.submodule1.test',
                               'from': 'internal',
                               'import': ['test']}],
                  'source_index': 3,
                  'source_name': 'internal.submodule1.test',
                  'target_index': 0,
                  'target_name': 'internal.__init__'},
                 {'cardinal': 1,
                  'imports': [{'by': 'internal.submodule2.test',
                               'from': 'internal.submodule2.test2',
                               'import': ['someclass']}],
                  'source_index': 4,
                  'source_name': 'internal.submodule2.test',
                  'target_index': 7,
                  'target_name': 'internal.submodule2.test2'},
                 {'cardinal': 1,
                  'imports': [{'by': 'internal.test',
                               'from': 'internal',
                               'import': ['submodule2']}],
                  'source_index': 5,
                  'source_name': 'internal.test',
                  'target_index': 0,
                  'target_name': 'internal.__init__'},
                 {'cardinal': 1,
                  'imports': [{'by': 'internal.test',
                               'from': 'internal.submodule1',
                               'import': ['submoduleA']}],
                  'source_index': 6,
                  'source_name': 'internal.test',
                  'target_index': 1,
                  'target_name': 'internal.submodule1.__init__'},
                 {'cardinal': 1,
                  'imports': [{'by': 'internal.test',
                               'from': 'internal.submodule1.submoduleA',
                               'import': ['test']}],
                  'source_index': 7,
                  'source_name': 'internal.test',
                  'target_index': 2,
                  'target_name': 'internal.submodule1.submoduleA.__init__'},
                 {'cardinal': 1,
                  'imports': [{'by': 'internal.test',
                               'from': 'internal.submodule2',
                               'import': ['doesnotexists']}],
                  'source_index': 8,
                  'source_name': 'internal.test',
                  'target_index': 5,
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
    pass

    def setUp(self):
        super(MatricesTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build_modules().build_imports().build_matrices()

    def assertEqualMatrices(self, dm, group):
        self.assertEqual(dm.get_matrix(1).depth, 1)
        self.assertEqual(dm.get_matrix(1).size, 1)
        self.assertEqual(dm.get_matrix(1).modules, {
            'internal': {'cardinal': {'exports': 18, 'imports': 18},
                         'group': {'index': 0, 'name': group},
                         'order': {'group': 0},
                         'similarity': {}}})
        self.assertEqual(dm.get_matrix(1).dependencies, [
            {'cardinal': 18,
             'imports': [
                 {'by': 'internal.submodule1.submoduleA.test',
                  'from': 'internal.test',
                  'import': [
                      'someclass',
                      'classA',
                      'classB',
                      'classC',
                      'classD',
                      'classE',
                      'classF',
                      'classG',
                      'classH']},
                 {'by': 'internal.submodule1.test',
                  'from': 'internal.submodule1.submoduleA',
                  'import': ['test', 'othertest']},
                 {'by': 'internal.submodule1.test',
                  'from': 'internal.submodule1.submoduleA.test',
                  'import': ['Test1']},
                 {'by': 'internal.submodule1.test',
                  'from': 'internal', 'import': ['test']},
                 {'by': 'internal.submodule2.test',
                  'from': 'internal.submodule2.test2',
                  'import': ['someclass']},
                 {'by': 'internal.test', 'from': 'internal',
                  'import': ['submodule2']},
                 {'by': 'internal.test',
                  'from': 'internal.submodule1',
                  'import': ['submoduleA']},
                 {'by': 'internal.test',
                  'from': 'internal.submodule1.submoduleA',
                  'import': ['test']},
                 {'by': 'internal.test',
                  'from': 'internal.submodule2',
                  'import': ['doesnotexists']}],
             'source_index': 0,
             'source_name': 'internal',
             'target_index': 0,
             'target_name': 'internal'}])
        self.assertEqual(dm.get_matrix(1).groups, [group])
        self.assertEqual(dm.get_matrix(1).keys, ['internal'])
        self.assertEqual(dm.get_matrix(1).matrix, [[18]])
        self.assertEqual(dm.get_matrix(2).depth, 2)
        self.assertEqual(dm.get_matrix(2).size, 4)
        self.assertEqual(dm.get_matrix(2).modules, {
            'internal.__init__': {
                'cardinal': {'exports': 2, 'imports': 9},
                'group': {'index': 0, 'name': group},
                'order': {'group': 0},
                'similarity': {}},
            'internal.submodule1': {
                'cardinal': {'exports': 5, 'imports': 5},
                'group': {'index': 0, 'name': group},
                'order': {'group': 1},
                'similarity': {}},
            'internal.submodule2': {
                'cardinal': {'exports': 2, 'imports': 3},
                'group': {'index': 0, 'name': group},
                'order': {'group': 2},
                'similarity': {}},
            'internal.test': {
                'cardinal': {'exports': 9, 'imports': 1},
                'group': {'index': 0, 'name': group},
                'order': {'group': 3},
                'similarity': {}}})
        self.assertEqual(dm.get_matrix(2).dependencies, [
            {'cardinal': 9,
             'imports': [{'by': 'internal.submodule1.submoduleA.test',
                          'from': 'internal.test',
                          'import': ['someclass',
                                     'classA',
                                     'classB',
                                     'classC',
                                     'classD',
                                     'classE',
                                     'classF',
                                     'classG',
                                     'classH']}],
             'source_index': 0,
             'source_name': 'internal.__init__',
             'target_index': 3,
             'target_name': 'internal.test'},
            {'cardinal': 3,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal.submodule1.submoduleA',
                          'import': ['test', 'othertest']},
                         {'by': 'internal.submodule1.test',
                          'from': 'internal.submodule1.submoduleA.test',
                          'import': ['Test1']}],
             'source_index': 1,
             'source_name': 'internal.submodule1',
             'target_index': 1,
             'target_name': 'internal.submodule1'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal',
                          'import': ['test']}],
             'source_index': 1,
             'source_name': 'internal.submodule1',
             'target_index': 0,
             'target_name': 'internal.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule2.test',
                          'from': 'internal.submodule2.test2',
                          'import': ['someclass']}],
             'source_index': 1,
             'source_name': 'internal.submodule1',
             'target_index': 2,
             'target_name': 'internal.submodule2'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal',
                          'import': ['submodule2']}],
             'source_index': 2,
             'source_name': 'internal.submodule2',
             'target_index': 0,
             'target_name': 'internal.__init__'},
            {'cardinal': 2,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule1',
                          'import': ['submoduleA']},
                         {'by': 'internal.test',
                          'from': 'internal.submodule1.submoduleA',
                          'import': ['test']}],
             'source_index': 2,
             'source_name': 'internal.submodule2',
             'target_index': 1,
             'target_name': 'internal.submodule1'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule2',
                          'import': ['doesnotexists']}],
             'source_index': 3,
             'source_name': 'internal.test',
             'target_index': 2,
             'target_name': 'internal.submodule2'}])
        self.assertEqual(dm.get_matrix(2).groups, [group, group, group, group])
        self.assertEqual(dm.get_matrix(2).keys, ['internal.__init__',
                                                 'internal.submodule1',
                                                 'internal.submodule2',
                                                 'internal.test'])
        self.assertEqual(
            dm.get_matrix(2).matrix,
            [[0, 0, 0, 9], [1, 3, 1, 0], [1, 2, 0, 0], [0, 0, 1, 0]])
        self.assertEqual(dm.get_matrix(3).depth, 3)
        self.assertEqual(dm.get_matrix(3).size, 8)
        self.assertEqual(dm.get_matrix(3).modules, {
            'internal.__init__': {
                'cardinal': {'exports': 2, 'imports': 9},
                'group': {'index': 0, 'name': group},
                'order': {'group': 0},
                'similarity': {}},
            'internal.submodule1.__init__': {
                'cardinal': {'exports': 1, 'imports': 2},
                'group': {'index': 0, 'name': group},
                'order': {'group': 1},
                'similarity': {}},
            'internal.submodule1.submoduleA': {
                'cardinal': {'exports': 4, 'imports': 2},
                'group': {'index': 0, 'name': group},
                'order': {'group': 2},
                'similarity': {}},
            'internal.submodule1.test': {
                'cardinal': {'exports': 0, 'imports': 1},
                'group': {'index': 0, 'name': group},
                'order': {'group': 3},
                'similarity': {}},
            'internal.submodule2.__init__': {
                'cardinal': {'exports': 1, 'imports': 1},
                'group': {'index': 0, 'name': group},
                'order': {'group': 4},
                'similarity': {}},
            'internal.submodule2.test': {
                'cardinal': {'exports': 0, 'imports': 1},
                'group': {'index': 0, 'name': group},
                'order': {'group': 5},
                'similarity': {}},
            'internal.submodule2.test2': {
                'cardinal': {'exports': 1, 'imports': 1},
                'group': {'index': 0, 'name': group},
                'order': {'group': 6},
                'similarity': {}},
            'internal.test': {'cardinal': {'exports': 9, 'imports': 1},
                              'group': {'index': 0, 'name': group},
                              'order': {'group': 7},
                              'similarity': {}}})
        self.assertEqual(dm.get_matrix(3).dependencies, [
            {'cardinal': 9,
             'imports': [
                 {'by': 'internal.submodule1.submoduleA.test',
                  'from': 'internal.test',
                  'import': ['someclass',
                             'classA',
                             'classB',
                             'classC',
                             'classD',
                             'classE',
                             'classF',
                             'classG',
                             'classH']}],
             'source_index': 0,
             'source_name': 'internal.__init__',
             'target_index': 7,
             'target_name': 'internal.test'},
            {'cardinal': 2,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal.submodule1.submoduleA',
                          'import': ['test', 'othertest']}],
             'source_index': 1,
             'source_name': 'internal.submodule1.__init__',
             'target_index': 2,
             'target_name': 'internal.submodule1.submoduleA'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal.submodule1.submoduleA.test',
                          'import': ['Test1']}],
             'source_index': 2,
             'source_name': 'internal.submodule1.submoduleA',
             'target_index': 2,
             'target_name': 'internal.submodule1.submoduleA'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal',
                          'import': ['test']}],
             'source_index': 2,
             'source_name': 'internal.submodule1.submoduleA',
             'target_index': 0,
             'target_name': 'internal.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule2.test',
                          'from': 'internal.submodule2.test2',
                          'import': ['someclass']}],
             'source_index': 3,
             'source_name': 'internal.submodule1.test',
             'target_index': 6,
             'target_name': 'internal.submodule2.test2'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal',
                          'import': ['submodule2']}],
             'source_index': 4,
             'source_name': 'internal.submodule2.__init__',
             'target_index': 0,
             'target_name': 'internal.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule1',
                          'import': ['submoduleA']}],
             'source_index': 5,
             'source_name': 'internal.submodule2.test',
             'target_index': 1,
             'target_name': 'internal.submodule1.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule1.submoduleA',
                          'import': ['test']}],
             'source_index': 6,
             'source_name': 'internal.submodule2.test2',
             'target_index': 2,
             'target_name': 'internal.submodule1.submoduleA'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule2',
                          'import': ['doesnotexists']}],
             'source_index': 7,
             'source_name': 'internal.test',
             'target_index': 4,
             'target_name': 'internal.submodule2.__init__'}])
        self.assertEqual(dm.get_matrix(3).groups,
                         [group, group, group, group, group, group, group,
                          group])
        self.assertEqual(dm.get_matrix(3).keys,
                         ['internal.__init__',
                          'internal.submodule1.__init__',
                          'internal.submodule1.submoduleA',
                          'internal.submodule1.test',
                          'internal.submodule2.__init__',
                          'internal.submodule2.test',
                          'internal.submodule2.test2',
                          'internal.test'])
        self.assertEqual(dm.get_matrix(3).matrix,
                         [[0, 0, 0, 0, 0, 0, 0, 9],
                          [0, 0, 2, 0, 0, 0, 0, 0],
                          [1, 0, 1, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 1, 0],
                          [1, 0, 0, 0, 0, 0, 0, 0],
                          [0, 1, 0, 0, 0, 0, 0, 0],
                          [0, 0, 1, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 1, 0, 0, 0]])
        self.assertEqual(dm.get_matrix(4).depth, 4)
        self.assertEqual(dm.get_matrix(4).size, 9)
        self.assertEqual(dm.get_matrix(4).modules, {
            'internal.__init__': {
                'cardinal': {'exports': 2, 'imports': 0},
                'group': {'index': 0, 'name': group},
                'order': {'group': 0},
                'similarity': {}},
            'internal.submodule1.__init__': {
                'cardinal': {'exports': 1, 'imports': 0},
                'group': {'index': 0, 'name': group},
                'order': {'group': 1},
                'similarity': {}},
            'internal.submodule1.submoduleA.__init__': {
                'cardinal': {'exports': 3,
                             'imports': 0},
                'group': {'index': 0, 'name': group},
                'order': {'group': 2},
                'similarity': {}},
            'internal.submodule1.submoduleA.test': {
                'cardinal': {'exports': 1,
                             'imports': 9},
                'group': {'index': 0, 'name': group},
                'order': {'group': 3},
                'similarity': {}},
            'internal.submodule1.test': {
                'cardinal': {'exports': 0, 'imports': 4},
                'group': {'index': 0, 'name': group},
                'order': {'group': 4},
                'similarity': {}},
            'internal.submodule2.__init__': {
                'cardinal': {'exports': 1, 'imports': 0},
                'group': {'index': 0, 'name': group},
                'order': {'group': 5},
                'similarity': {}},
            'internal.submodule2.test': {
                'cardinal': {'exports': 0, 'imports': 1},
                'group': {'index': 0, 'name': group},
                'order': {'group': 6},
                'similarity': {}},
            'internal.submodule2.test2': {
                'cardinal': {'exports': 1, 'imports': 0},
                'group': {'index': 0, 'name': group},
                'order': {'group': 7},
                'similarity': {}},
            'internal.test': {'cardinal': {'exports': 9, 'imports': 4},
                              'group': {'index': 0, 'name': group},
                              'order': {'group': 8},
                              'similarity': {}}})
        self.assertEqual(dm.get_matrix(4).dependencies, [
            {'cardinal': 9,
             'imports': [{'by': 'internal.submodule1.submoduleA.test',
                          'from': 'internal.test',
                          'import': ['someclass',
                                     'classA',
                                     'classB',
                                     'classC',
                                     'classD',
                                     'classE',
                                     'classF',
                                     'classG',
                                     'classH']}],
             'source_index': 0,
             'source_name': 'internal.submodule1.submoduleA.test',
             'target_index': 8,
             'target_name': 'internal.test'},
            {'cardinal': 2,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal.submodule1.submoduleA',
                          'import': ['test', 'othertest']}],
             'source_index': 1,
             'source_name': 'internal.submodule1.test',
             'target_index': 2,
             'target_name': 'internal.submodule1.submoduleA.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal.submodule1.submoduleA.test',
                          'import': ['Test1']}],
             'source_index': 2,
             'source_name': 'internal.submodule1.test',
             'target_index': 3,
             'target_name': 'internal.submodule1.submoduleA.test'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule1.test',
                          'from': 'internal',
                          'import': ['test']}],
             'source_index': 3,
             'source_name': 'internal.submodule1.test',
             'target_index': 0,
             'target_name': 'internal.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.submodule2.test',
                          'from': 'internal.submodule2.test2',
                          'import': ['someclass']}],
             'source_index': 4,
             'source_name': 'internal.submodule2.test',
             'target_index': 7,
             'target_name': 'internal.submodule2.test2'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal',
                          'import': ['submodule2']}],
             'source_index': 5,
             'source_name': 'internal.test',
             'target_index': 0,
             'target_name': 'internal.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule1',
                          'import': ['submoduleA']}],
             'source_index': 6,
             'source_name': 'internal.test',
             'target_index': 1,
             'target_name': 'internal.submodule1.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule1.submoduleA',
                          'import': ['test']}],
             'source_index': 7,
             'source_name': 'internal.test',
             'target_index': 2,
             'target_name': 'internal.submodule1.submoduleA.__init__'},
            {'cardinal': 1,
             'imports': [{'by': 'internal.test',
                          'from': 'internal.submodule2',
                          'import': ['doesnotexists']}],
             'source_index': 8,
             'source_name': 'internal.test',
             'target_index': 5,
             'target_name': 'internal.submodule2.__init__'}])
        self.assertEqual(
            dm.get_matrix(4).groups,
            [group, group, group, group, group, group, group, group, group])
        self.assertEqual(dm.get_matrix(4).keys,
                         ['internal.__init__',
                          'internal.submodule1.__init__',
                          'internal.submodule1.submoduleA.__init__',
                          'internal.submodule1.submoduleA.test',
                          'internal.submodule1.test',
                          'internal.submodule2.__init__',
                          'internal.submodule2.test',
                          'internal.submodule2.test2',
                          'internal.test'])
        self.assertEqual(dm.get_matrix(4).matrix,
                         [[0, 0, 0, 0, 0, 0, 0, 0, 9],
                          [0, 0, 2, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 1, 0, 0, 0, 0, 0],
                          [1, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 1, 0],
                          [1, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 1, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 1, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 1, 0, 0, 0]])

    def test_matrices(self):
        # local_path = os.path.abspath(os.path.join(
        #     os.path.dirname(os.path.dirname(__file__)), 'tests'))
        for dm in [self.str_dm, self.list_dm]:
            self.assertEqualMatrices(dm, '')
        self.assertEqualMatrices(self.od_dm, 'Only group')
        for dm in [self.str_dm, self.list_dm]:
            self.assertEqual(dm.get_matrix(0), dm.get_matrix(dm.max_depth))
            self.assertEqual(dm.get_matrix(dm.max_depth),
                             dm.get_matrix(dm.max_depth + 1))
            self.assertEqual(dm.get_matrix(1), dm.get_matrix(-1))

            for i in range(1, dm.max_depth - 1):
                self.assertNotEqual(dm.get_matrix(i), dm.get_matrix(i + 1))


class OutputTestCase(AbstractTestCase):
    def setUp(self):
        super(OutputTestCase, self).setUp()
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            dm.build()

    # def test_load_json_dump(self):
    #     for dm in [self.str_dm, self.list_dm, self.od_dm]:
    #         data = json.loads(dm.to_json())
    #
    #         obj = DependencyMatrix(data['packages'])
    #         obj.groups = data['groups']
    #         obj.modules = data['modules']
    #         obj.imports = data['imports']
    #         obj.matrices = data['matrices']
    #         obj.max_depth = data['max_depth']
    #         obj._inside = data['_inside']
    #         obj._modules_are_built = data['_modules_are_built']
    #         obj._imports_are_built = data['_imports_are_built']
    #         obj._matrices_are_built = data['_matrices_are_built']
    #         self.assertEqual(dm, obj, 'JSON dump/load/assign')
    #
    #         obj2 = DependencyMatrix(data['packages'])
    #         obj2.groups = data['groups']
    #         obj2.build()
    #         self.assertEqual(dm, obj2, 'JSON dump/load/build')

    def test_matrix_to_json(self):
        class Dummy(object):
            pass

        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            for i in range(1, dm.max_depth):
                data = json.loads(dm.get_matrix(i).to_json())
                other = Dummy()
                other.depth = data['depth']
                other.size = data['size']
                other.modules = data['modules']
                other.dependencies = data['dependencies']
                other.keys = data['keys']
                other.groups = data['groups']
                other.matrix = data['matrix']
                self.assertEqual(dm.get_matrix(i),
                                 other, 'JSON MATRIX dump/load %s' % i)

    def test_matrix_to_csv(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(
                dm.get_matrix(1).to_csv(),
                ',internal\r\n'
                'internal,18',
                'CSV MATRIX 1')
            self.assertEqual(
                dm.get_matrix(2).to_csv(),
                ',internal.__init__,internal.submodule1,'
                'internal.submodule2,internal.test\r\n'
                'internal.__init__,0,0,0,9\r\n'
                'internal.submodule1,1,3,1,0\r\n'
                'internal.submodule2,1,2,0,0\r\n'
                'internal.test,0,0,1,0',
                'CSV MATRIX 2')
            self.assertEqual(
                dm.get_matrix(3).to_csv(),
                ',internal.__init__,internal.submodule1.__init__,'
                'internal.submodule1.submoduleA,internal.submodule1.test,'
                'internal.submodule2.__init__,internal.submodule2.test,'
                'internal.submodule2.test2,internal.test\r\n'
                'internal.__init__,0,0,0,0,0,0,0,9\r\n'
                'internal.submodule1.__init__,0,0,2,0,0,0,0,0\r\n'
                'internal.submodule1.submoduleA,1,0,1,0,0,0,0,0\r\n'
                'internal.submodule1.test,0,0,0,0,0,0,1,0\r\n'
                'internal.submodule2.__init__,1,0,0,0,0,0,0,0\r\n'
                'internal.submodule2.test,0,1,0,0,0,0,0,0\r\n'
                'internal.submodule2.test2,0,0,1,0,0,0,0,0\r\n'
                'internal.test,0,0,0,0,1,0,0,0',
                'CSV MATRIX 3')
            self.assertEqual(
                dm.get_matrix(4).to_csv(),
                ',internal.__init__,internal.submodule1.__init__,'
                'internal.submodule1.submoduleA.__init__,'
                'internal.submodule1.submoduleA.test,internal.submodule1.test,'
                'internal.submodule2.__init__,internal.submodule2.test,'
                'internal.submodule2.test2,internal.test\r\n'
                'internal.__init__,0,0,0,0,0,0,0,0,9\r\n'
                'internal.submodule1.__init__,0,0,2,0,0,0,0,0,0\r\n'
                'internal.submodule1.submoduleA.__init__,0,0,0,1,0,0,0,0,0\r\n'
                'internal.submodule1.submoduleA.test,1,0,0,0,0,0,0,0,0\r\n'
                'internal.submodule1.test,0,0,0,0,0,0,0,1,0\r\n'
                'internal.submodule2.__init__,1,0,0,0,0,0,0,0,0\r\n'
                'internal.submodule2.test,0,1,0,0,0,0,0,0,0\r\n'
                'internal.submodule2.test2,0,0,1,0,0,0,0,0,0\r\n'
                'internal.test,0,0,0,0,0,1,0,0,0',
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
