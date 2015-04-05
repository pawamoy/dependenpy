# -*- coding: utf-8 -*-

# Copyright (c) 2015 Timothée Mazzucotelli
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals
from builtins import range
from builtins import object

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import unittest
import json
from collections import OrderedDict
from dependenpy.utils import MatrixBuilder


class AbstractTestCase(unittest.TestCase):
    def setUp(self):
        str_p = 'internal'
        list_p = ['internal']
        od_p = ['Only group', ['internal']]

        self.str_dm = MatrixBuilder(str_p)
        self.list_dm = MatrixBuilder(list_p)
        self.od_dm = MatrixBuilder(od_p)

    def tearDown(self):
        del self.str_dm
        del self.list_dm
        del self.od_dm


class EmptyTestCase(AbstractTestCase):
    def test_wrong_type(self):
        tmp = MatrixBuilder('')
        self.assertRaises(AttributeError, tmp.__init__, 1)

    def test_wrong_list(self):
        tmp = MatrixBuilder('')
        self.assertRaises(AttributeError, tmp.__init__, ['', '', ['']])
        self.assertRaises(AttributeError, tmp.__init__, ['', '', [''], ['']])
        self.assertRaises(AttributeError, tmp.__init__, ['', [''], [''], ''])
        self.assertRaises(AttributeError, tmp.__init__, [[''], ''])

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
        self.dm = MatrixBuilder('unfoundable')

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
        self.assertEqual(dm.get_matrix(1).modules, OrderedDict([(u'internal', {
            u'cardinal': {u'imports': 19, u'exports': 19},
            u'group': {u'index': 0, u'name': group}, u'name': u'internal',
            u'order': {u'import': {}, u'similarity': {}, u'export': {},
                       u'name': {}, u'group': {False: 0, True: 0}}})]))
        self.assertEqual(dm.get_matrix(1).dependencies, [
            {u'cardinal': 19,
             u'imports': [{u'by': u'internal.submodule1.submoduleA.test',
                           u'from': u'internal.test',
                           u'import': [
                               'someclass',
                               'classA',
                               'classB',
                               'classC',
                               'classD',
                               'classE',
                               'classF',
                               'classG',
                               'classH']},
                          {u'by': u'internal.submodule1.test',
                           u'from': u'internal.submodule1.submoduleA',
                           u'import': [
                               'test',
                               'othertest']},
                          {u'by': u'internal.submodule1.test',
                           u'from': u'internal.submodule1.submoduleA.test',
                           u'import': [
                               'Test1']},
                          {u'by': u'internal.submodule1.test',
                           u'from': u'internal',
                           u'import': [
                               'test']},
                          {u'by': u'internal.submodule2.test',
                           u'from': u'internal.submodule2.test2',
                           u'import': [
                               'someclass']},
                          {u'by': u'internal.submodule2.test',
                           u'from': 'internal.submodule1.submoduleA',
                           u'import': [
                               'othertest']},
                          {u'by': u'internal.test',
                           u'from': 'internal',
                           u'import': [
                               'submodule2']},
                          {u'by': u'internal.test',
                           u'from': 'internal.submodule1',
                           u'import': [
                               'submoduleA']},
                          {u'by': u'internal.test',
                           u'from': 'internal.submodule1.submoduleA',
                           u'import': [
                               'test']},
                          {u'by': u'internal.test',
                           u'from': 'internal.submodule2',
                           u'import': [
                               'doesnotexists']}],
             u'source_index': 0,
             u'source_name': u'internal',
             u'target_index': 0,
             u'target_name': u'internal'}])
        self.assertEqual(dm.get_matrix(1).groups, [group])
        self.assertEqual(dm.get_matrix(1).keys, ['internal'])
        self.assertEqual(dm.get_matrix(1).matrix, [[19]])
        self.assertEqual(dm.get_matrix(2).depth, 2)
        self.assertEqual(dm.get_matrix(2).size, 4)
        self.assertEqual(
            dm.get_matrix(2).modules,
            OrderedDict(
                [(u'internal.__init__', {
                    u'cardinal': {u'imports': 0, u'exports': 2},
                    u'group': {u'index': 0, u'name': group},
                    u'name': u'internal.__init__',
                    u'order': {u'import': {}, u'similarity': {}, u'export': {},
                               u'name': {}, u'group': {False: 0, True: 0}}}),
                 (u'internal.submodule1',
                  {u'cardinal': {u'imports': 13, u'exports': 6},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1',
                   u'order': {u'import': {}, u'similarity': {},
                              u'export': {},
                              u'name': {}, u'group': {False: 1, True: 1}}}),
                 (u'internal.submodule2',
                  {u'cardinal': {u'imports': 2, u'exports': 2},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule2',
                   u'order': {u'import': {}, u'similarity': {},
                              u'export': {},
                              u'name': {}, u'group': {False: 2, True: 2}}}),
                 (u'internal.test',
                  {u'cardinal': {u'imports': 4, u'exports': 9},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.test',
                   u'order': {u'import': {}, u'similarity': {},
                              u'export': {},
                              u'name': {},
                              u'group': {False: 3, True: 3}}})]))
        self.assertEqual(dm.get_matrix(2).dependencies, [
            {u'cardinal': 9,
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
             u'source_index': 1,
             u'source_name': u'internal.submodule1',
             u'target_index': 3,
             u'target_name': u'internal.test'},
            {u'cardinal': 3,
             u'imports': [{u'by': u'internal.submodule1.test',
                           u'from': u'internal.submodule1.submoduleA',
                           u'import': ['test', 'othertest']},
                          {u'by': u'internal.submodule1.test',
                           u'from': u'internal.submodule1.submoduleA.test',
                           u'import': ['Test1']}],
             u'source_index': 1,
             u'source_name': u'internal.submodule1',
             u'target_index': 1,
             u'target_name': u'internal.submodule1'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.submodule1.test',
                           u'from': u'internal',
                           u'import': ['test']}],
             u'source_index': 1,
             u'source_name': u'internal.submodule1',
             u'target_index': 0,
             u'target_name': u'internal.__init__'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.submodule2.test',
                           u'from': u'internal.submodule2.test2',
                           u'import': ['someclass']}],
             u'source_index': 2,
             u'source_name': u'internal.submodule2',
             u'target_index': 2,
             u'target_name': u'internal.submodule2'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.submodule2.test',
                           u'from': 'internal.submodule1.submoduleA',
                           u'import': ['othertest']}],
             u'source_index': 2,
             u'source_name': u'internal.submodule2',
             u'target_index': 1,
             u'target_name': u'internal.submodule1'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.test',
                           u'from': 'internal',
                           u'import': ['submodule2']}],
             u'source_index': 3,
             u'source_name': u'internal.test',
             u'target_index': 0,
             u'target_name': u'internal.__init__'},
            {u'cardinal': 2,
             u'imports': [{u'by': u'internal.test',
                           u'from': 'internal.submodule1',
                           u'import': ['submoduleA']},
                          {u'by': u'internal.test',
                           u'from': 'internal.submodule1.submoduleA',
                           u'import': ['test']}],
             u'source_index': 3,
             u'source_name': u'internal.test',
             u'target_index': 1,
             u'target_name': u'internal.submodule1'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.test',
                           u'from': 'internal.submodule2',
                           u'import': ['doesnotexists']}],
             u'source_index': 3,
             u'source_name': u'internal.test',
             u'target_index': 2,
             u'target_name': u'internal.submodule2'}])
        self.assertEqual(dm.get_matrix(2).groups, [group, group, group, group])
        self.assertEqual(dm.get_matrix(2).keys, ['internal.__init__',
                                                 'internal.submodule1',
                                                 'internal.submodule2',
                                                 'internal.test'])
        self.assertEqual(
            dm.get_matrix(2).matrix,
            [[0, 0, 0, 0], [1, 3, 0, 9], [0, 1, 1, 0], [1, 2, 1, 0]])
        self.assertEqual(dm.get_matrix(3).depth, 3)
        self.assertEqual(dm.get_matrix(3).size, 8)
        self.assertEqual(
            dm.get_matrix(3).modules,
            OrderedDict(
                [(u'internal.__init__',
                  {u'cardinal': {u'imports': 0, u'exports': 2},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.__init__',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 0, True: 0}}}),
                 (u'internal.submodule1.__init__',
                  {u'cardinal': {u'imports': 0, u'exports': 1},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1.__init__',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 1, True: 1}}}),
                 (u'internal.submodule1.submoduleA',
                  {u'cardinal': {u'imports': 9, u'exports': 5},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1.submoduleA',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 2, True: 2}}}),
                 (u'internal.submodule1.test',
                  {u'cardinal': {u'imports': 4, u'exports': 0},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1.test',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 3, True: 3}}}),
                 (u'internal.submodule2.__init__',
                  {u'cardinal': {u'imports': 0, u'exports': 1},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule2.__init__',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 4, True: 4}}}),
                 (u'internal.submodule2.test',
                  {u'cardinal': {u'imports': 2, u'exports': 0},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule2.test',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 5, True: 5}}}),
                 (u'internal.submodule2.test2',
                  {u'cardinal': {u'imports': 0, u'exports': 1},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule2.test2',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 6, True: 6}}}),
                 (u'internal.test',
                  {u'cardinal': {u'imports': 4, u'exports': 9},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.test',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 7, True: 7}}})]))
        self.assertEqual(dm.get_matrix(3).dependencies, [
            {u'cardinal': 9,
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
             u'source_index': 2,
             u'source_name': u'internal.submodule1.submoduleA',
             u'target_index': 7,
             u'target_name': u'internal.test'},
            {u'cardinal': 3,
             u'imports': [{u'by': u'internal.submodule1.test',
                           u'from': u'internal.submodule1.submoduleA',
                           u'import': ['test', 'othertest']},
                          {u'by': u'internal.submodule1.test',
                           u'from': u'internal.submodule1.submoduleA.test',
                           u'import': ['Test1']}],
             u'source_index': 3,
             u'source_name': u'internal.submodule1.test',
             u'target_index': 2,
             u'target_name': u'internal.submodule1.submoduleA'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.submodule1.test',
                           u'from': u'internal',
                           u'import': ['test']}],
             u'source_index': 3,
             u'source_name': u'internal.submodule1.test',
             u'target_index': 0,
             u'target_name': u'internal.__init__'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.submodule2.test',
                           u'from': u'internal.submodule2.test2',
                           u'import': ['someclass']}],
             u'source_index': 5,
             u'source_name': u'internal.submodule2.test',
             u'target_index': 6,
             u'target_name': u'internal.submodule2.test2'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.submodule2.test',
                           u'from': 'internal.submodule1.submoduleA',
                           u'import': ['othertest']}],
             u'source_index': 5,
             u'source_name': u'internal.submodule2.test',
             u'target_index': 2,
             u'target_name': u'internal.submodule1.submoduleA'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.test',
                           u'from': 'internal',
                           u'import': ['submodule2']}],
             u'source_index': 7,
             u'source_name': u'internal.test',
             u'target_index': 0,
             u'target_name': u'internal.__init__'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.test',
                           u'from': 'internal.submodule1',
                           u'import': ['submoduleA']}],
             u'source_index': 7,
             u'source_name': u'internal.test',
             u'target_index': 1,
             u'target_name': u'internal.submodule1.__init__'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.test',
                           u'from': 'internal.submodule1.submoduleA',
                           u'import': ['test']}],
             u'source_index': 7,
             u'source_name': u'internal.test',
             u'target_index': 2,
             u'target_name': u'internal.submodule1.submoduleA'},
            {u'cardinal': 1,
             u'imports': [{u'by': u'internal.test',
                           u'from': 'internal.submodule2',
                           u'import': ['doesnotexists']}],
             u'source_index': 7,
             u'source_name': u'internal.test',
             u'target_index': 4,
             u'target_name': u'internal.submodule2.__init__'}])
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
                         [[0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 9],
                          [1, 0, 3, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 1, 0, 0, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 0, 1, 0, 0, 0]])
        self.assertEqual(dm.get_matrix(4).depth, 4)
        self.assertEqual(dm.get_matrix(4).size, 9)
        self.assertEqual(
            dm.get_matrix(4).modules,
            OrderedDict(
                [(u'internal.__init__',
                  {u'cardinal': {u'imports': 0, u'exports': 2},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.__init__',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 0, True: 0}}}),
                 (u'internal.submodule1.__init__',
                  {u'cardinal': {u'imports': 0, u'exports': 1},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1.__init__',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 1, True: 1}}}),
                 (u'internal.submodule1.submoduleA.__init__',
                  {u'cardinal': {u'imports': 0, u'exports': 4},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1.submoduleA.__init__',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 2, True: 2}}}),
                 (u'internal.submodule1.submoduleA.test',
                  {u'cardinal': {u'imports': 9, u'exports': 1},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1.submoduleA.test',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 3, True: 3}}}),
                 (u'internal.submodule1.test',
                  {u'cardinal': {u'imports': 4, u'exports': 0},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule1.test',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 4, True: 4}}}),
                 (u'internal.submodule2.__init__',
                  {u'cardinal': {u'imports': 0, u'exports': 1},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule2.__init__',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 5, True: 5}}}),
                 (u'internal.submodule2.test',
                  {u'cardinal': {u'imports': 2, u'exports': 0},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule2.test',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 6, True: 6}}}),
                 (u'internal.submodule2.test2',
                  {u'cardinal': {u'imports': 0, u'exports': 1},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.submodule2.test2',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 7, True: 7}}}),
                 (u'internal.test',
                  {u'cardinal': {u'imports': 4, u'exports': 9},
                   u'group': {u'index': 0, u'name': group},
                   u'name': u'internal.test',
                   u'order': {u'import': {}, u'similarity': {}, u'export': {},
                              u'name': {}, u'group': {False: 8, True: 8}}})]))
        self.assertEqual(dm.get_matrix(4).dependencies, [
            {u'cardinal': 9,
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
                         [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 9],
                          [1, 0, 2, 1, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 1, 0, 0, 0, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 0, 0, 1, 0, 0, 0]])

    def test_matrices(self):
        # local_path = os.path.abspath(os.path.join(
        # os.path.dirname(os.path.dirname(__file__)), 'tests'))
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
    # for dm in [self.str_dm, self.list_dm, self.od_dm]:
    # data = json.loads(dm.to_json())
    #
    # obj = MatrixBuilder(data['packages'])
    # obj.groups = data['groups']
    # obj.modules = data['modules']
    # obj.imports = data['imports']
    # obj.matrices = data['matrices']
    # obj.max_depth = data['max_depth']
    # obj._inside = data['_inside']
    # obj._modules_are_built = data['_modules_are_built']
    # obj._imports_are_built = data['_imports_are_built']
    # obj._matrices_are_built = data['_matrices_are_built']
    # self.assertEqual(dm, obj, 'JSON dump/load/assign')
    #
    # obj2 = MatrixBuilder(data['packages'])
    # obj2.groups = data['groups']
    # obj2.build()
    # self.assertEqual(dm, obj2, 'JSON dump/load/build')

    # def test_matrix_to_json(self):
    #     class Dummy(object):
    #         pass
    #
    #     for dm in [self.str_dm, self.list_dm, self.od_dm]:
    #         for i in range(1, dm.max_depth):
    #             data = json.loads(dm.get_matrix(i).to_json())
    #             other = Dummy()
    #             other.depth = data['depth']
    #             other.size = data['size']
    #             other.modules = data['modules']
    #             other.dependencies = data['dependencies']
    #             other.keys = data['keys']
    #             other.groups = data['groups']
    #             other.matrix = data['matrix']
    #             self.assertEqual(dm.get_matrix(i),
    #                              other, 'JSON MATRIX dump/load %s' % i)

    def test_matrix_to_csv(self):
        for dm in [self.str_dm, self.list_dm, self.od_dm]:
            self.assertEqual(
                dm.get_matrix(1).to_csv(),
                ',internal\r\n'
                'internal,19',
                'CSV MATRIX 1')
            self.assertEqual(
                dm.get_matrix(2).to_csv(),
                ',internal.__init__,internal.submodule1,'
                'internal.submodule2,internal.test\r\n'
                'internal.__init__,0,0,0,0\r\n'
                'internal.submodule1,1,3,0,9\r\n'
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
                u'internal.submodule1.test,1,0,3,0,0,0,0,0\r\n'
                u'internal.submodule2.__init__,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule2.test,0,0,1,0,0,0,1,0\r\n'
                u'internal.submodule2.test2,0,0,0,0,0,0,0,0\r\n'
                u'internal.test,1,1,1,0,1,0,0,0',
                'CSV MATRIX 3')
            self.assertEqual(
                dm.get_matrix(4).to_csv(),
                u',internal.__init__,internal.submodule1.__init__,'
                u'internal.submodule1.submoduleA.__init__,'
                u'internal.submodule1.submoduleA.test,internal.submodule1.test,'
                u'internal.submodule2.__init__,internal.submodule2.test,'
                u'internal.submodule2.test2,internal.test\r\n'
                u'internal.__init__,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule1.__init__,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule1.submoduleA.__init__,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule1.submoduleA.test,0,0,0,0,0,0,0,0,9\r\n'
                u'internal.submodule1.test,1,0,2,1,0,0,0,0,0\r\n'
                u'internal.submodule2.__init__,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.submodule2.test,0,0,1,0,0,0,0,1,0\r\n'
                u'internal.submodule2.test2,0,0,0,0,0,0,0,0,0\r\n'
                u'internal.test,1,1,1,0,0,1,0,0,0',
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
