"""
Created on 8 janv. 2015

@author: Pierre.Parrend
"""

import unittest
from archan.archan import Archan
from archan.dsm import DesignStructureMatrix


class TestArchan(unittest.TestCase):

    def setUp(self):
        web_app_categories = ['app_module', 'app_module', 'app_module',
                              'app_module', 'broker',
                              'app_lib', 'data', 'data',
                              'data', 'framework', 'framework']
        web_app_entities = ['store', 'personal_information', 'order',
                            'payment', 'available_services',
                            'store_lib', 'store_data', 'client_data',
                            'order_data', 'framework', 'login']
        web_app_dsm = [[1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
                       [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                       [0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0],
                       [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0],
                       [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],  # broker
                       [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]]
        self.web_app_dependency_matrix = DesignStructureMatrix(
            web_app_categories, web_app_entities, web_app_dsm)
        genida_categories = ['framework',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'app_lib',
                             'app_lib', 'app_module', 'app_lib',
                             'app_lib', 'app_lib', 'app_module',
                             'app_module', 'app_module', 'app_module',
                             'app_module', 'broker']

        genida_entities = ['django',
                           'axes', 'modeltranslation', 'suit',
                           'markdown_deux', 'cities_light', 'avatar',
                           'djangobower', 'rosetta', 'imagekit',
                           'smart_selects', 'captcha', 'datetimewidget',
                           'django_forms_bootstrap', 'pagedown', 'dataforms',
                           'graph', 'news', 'cs_models',
                           'zxcvbn_password', 'dependenpy', 'complex',
                           'questionnaires', 'members', 'genida',
                           'security', 'services']

        genida_dsm = [[4438, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [30, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [50, 0, 41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [41, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [43, 0, 0, 0, 0, 45, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [32, 0, 0, 0, 0, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [12, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [36, 0, 0, 0, 0, 0, 0, 0, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [33, 0, 0, 0, 0, 0, 0, 0, 0, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [75, 0, 2, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 97, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
                      [12, 0, 2, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 1, 0, 0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                      [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [13, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 7, 0, 0, 0, 0, 1],
                      [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                      [22, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                      [26, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
                      [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1]]
        self.genida_dm = DesignStructureMatrix(
            genida_categories, genida_entities, genida_dsm)

    # TODO: set -1 for items NOT to be considered
    # 0 for items which MUST NOT be present
    # 1 for items which MUST be present
    # TODO: validate and check validity!!
    completeMediationMatrixOnlineStore = [
        [-1, 0, 0, 0, 1, -1, -1, -1, -1, -1, -1],  # app modules
        [0, -1, 0, 0, 1, -1, -1, -1, -1, -1, -1],
        [0, 0, -1, 0, 1, -1, -1, -1, -1, -1, -1],
        [0, 0, 0, -1, 1, -1, -1, -1, -1, -1, -1],
        [1, 1, 1, 1, -1, 0, 0, 0, 0, -1, -1],  # broker
        [0, 0, 0, 0, 0, -1, 0, 0, 0, -1, -1],  # libs
        [0, 0, 0, 0, 0, 0, -1, 0, 0, -1, -1],  # data
        [0, 0, 0, 0, 0, 0, 0, -1, 0, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1],  # framework
        [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1]]  # framework

    # generated matrix - for reference and visualization
    completeMediationMatrixGenida = [
        [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, -1, 0, 0, 0, 1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, -1, 0, 0, 1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, -1, 0, 1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0, -1, 1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 1, 1, 1, 1, -1],
    ]

    def test_mediation_matrix_generation(self):
        archan = Archan()
        # referenceDSM = self.web_app_dependency_matrix.getDependencyMatrix()
        reference_mediation_matrix = self.complete_mediation_matrix_online_store
        generate_mediation_matrix = archan.generate_mediation_matrix(
            self.web_app_dependency_matrix)

        generation_complete = True
        for i in range(1, self.web_app_dependency_matrix.getSize()):
            for j in range(1, self.web_app_dependency_matrix.getSize()):
                if reference_mediation_matrix[i][j] != generate_mediation_matrix[i][j]:
                    generation_complete = False
                    print("Error in generation of the compliance matrix at " + str(i) + ":" + str(j))

        self.assertTrue(generation_complete)

    def test_complete_mediation(self):
        print("""*** Test Archan 'complete mediation' / online store ***""")
        archan = Archan()
        compliant = archan.check_complete_mediation(
            self.web_app_dependency_matrix)
        if compliant:
            print("Complete Mediation is enforced")
        else:
            print("Complete Mediation is NOT enforced")
        self.assertTrue(compliant)

    def test_economy_of_mechanism(self):
        print("""*** Test Archan 'Economy of Mechanism' ***""")
        archan = Archan()
        economy_of_mechanism = archan.check_economy_of_mechanism(
            self.web_app_dependency_matrix)
        if economy_of_mechanism:
            print("Economy of Mechanism is enforced")
        else:
            print("Economy of Mechanism is NOT enforced")
        self.assertTrue(economy_of_mechanism)

    def test_least_common_mechanism(self):
        print("""*** Test Archan 'Least common Mechanism' ***""")
        archan = Archan()
        least_common_mechanism = archan.check_least_common_mechanism(
            self.web_app_dependency_matrix)
        if least_common_mechanism:
            print("Least common Mechanism is enforced")
        else:
            print("Least common Mechanism is NOT enforced")
        self.assertTrue(least_common_mechanism)

    def test_open_design(self):
        print("""*** Test Archan 'Open Design' ***""")
        archan = Archan()
        open_design = archan.check_open_design()
        if open_design:
            print("Open Design is enforced")
        else:
            print("Open Design is NOT enforced")
        self.assertTrue(open_design)

    # Test Genida
    def test_economy_of_mechanism_genida(self):
        print("""*** Test Archan for Genida 'Economy of Mechanism' ***""")
        archan = Archan()
        economy_of_mechanism = archan.check_economy_of_mechanism(
            self.genida_dm)
        if economy_of_mechanism:
            print("Economy of Mechanism is enforced for Genida")
        else:
            print("Economy of Mechanism is NOT enforced for Genida")
        self.assertTrue(economy_of_mechanism)

    def test_least_common_mechanism_genida(self):
        print("""*** Test Archan for Genida 'Least common Mechanism' ***""")
        archan = Archan()
        least_common_mechanism = archan.check_least_common_mechanism(
            self.genida_dm)
        if least_common_mechanism:
            print("Least common Mechanism is enforced for Genida")
        else:
            print("Least common Mechanism is NOT enforced for Genida")
        self.assertTrue(least_common_mechanism)

    def test_complete_mediation_genida(self):
        print("""*** Test Archan for Genida 'complete mediation'
        / online store ***""")
        archan = Archan()
        compliant = archan.check_complete_mediation(self.genida_dm)
        if compliant:
            print("Complete Mediation is enforced for Genida")
        else:
            print("Complete Mediation is NOT enforced for Genida")
        self.assertTrue(compliant)

    def test_code_clean(self):
        archan = Archan()
        self.assertTrue(archan.checkCodeClean())
