'''
Created on 8 janv. 2015

@author: Pierre.Parrend
'''
import unittest
from fr.unistra.icube_bfo.archan.archan import Archan
from fr.unistra.icube_bfo.archan.dsm import DesignStructureMatrix


class TestArchan(unittest.TestCase):

    def setUp(self):
        webAppCategories = ['app_module', 'app_module', 'app_module',
                            'app_module', 'broker',
                            'app_lib', 'data', 'data',
                            'data', 'framework', 'framework']
        webAppEntities = ['store', 'personal_information', 'order',
                          'payment', 'available_services',
                          'store_lib', 'store_data', 'client_data',
                          'order_data', 'framework', 'login']
        webAppDsm = [[1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
                     [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                     [0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0],
                     [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0],
                     [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],#broker
                     [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]]
        self.webAppDependencyMatrix = DesignStructureMatrix(webAppCategories,
                                                            webAppEntities,
                                                            webAppDsm)
        genidaCategories = ['framework',
                            'core_lib', 'core_lib', 'core_lib',
                            'core_lib', 'core_lib', 'core_lib',
                            'core_lib', 'core_lib', 'core_lib',
                            'core_lib', 'core_lib', 'core_lib',
                            'core_lib', 'core_lib', 'app_lib',
                            'app_lib', 'app_module', 'app_lib',
                            'app_lib', 'app_lib', 'app_module',
                            'app_module', 'app_module', 'app_module',
                            'app_module', 'broker']

        genidaEntities = ['django',
                          'axes', 'modeltranslation', 'suit',
                          'markdown_deux', 'cities_light', 'avatar',
                          'djangobower', 'rosetta', 'imagekit',
                          'smart_selects', 'captcha', 'datetimewidget',
                          'django_forms_bootstrap', 'pagedown', 'dataforms',
                          'graph', 'news', 'cs_models',
                          'zxcvbn_password', 'dependenpy', 'complex',
                          'questionnaires', 'members', 'genida',
                          'security', 'services']
        # Remark: djanog/django dependencies not quantified
        genidaDsm = [[100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1],
]
        self.genidaDM = DesignStructureMatrix(genidaCategories,
                                              genidaEntities,
                                              genidaDsm)

    # TODO: set -1 for items NOT to be considered
    # 0 for items which MUST NOT be present
    # 1 for items which MUST be present
    # TODO: validate and check validity!!
    completeMediationMatrixOnlineStore = [[-1, 0, 0, 0, 1, -1, -1, -1, -1, -1, -1],# app modules
                                          [0, -1, 0, 0, 1, -1, -1, -1, -1, -1, -1],
                                          [0, 0, -1, 0, 1, -1, -1, -1, -1, -1, -1],
                                          [0, 0, 0, -1, 1, -1, -1, -1, -1, -1, -1],
                                          [1, 1, 1, 1, -1, 0, 0, 0, 0, -1, -1],# broker
                                          [0, 0, 0, 0, 0, -1, 0, 0, 0, -1, -1],# libs
                                          [0, 0, 0, 0, 0, 0, -1, 0, 0, -1, -1],# data
                                          [0, 0, 0, 0, 0, 0, 0, -1, 0, -1, -1],
                                          [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
                                          [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1],# framework
                                          [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1]]# framework

    # generated matrix - for reference and visualization
    completeMediationMatrixGenida = [[-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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

    def testMediationMatrixGeneration(self):
        archan = Archan()
        # referenceDSM = self.webAppDependencyMatrix.getDependencyMatrix()
        referenceMediationMatrix = self.completeMediationMatrixOnlineStore
        generatedMediationMatrix = archan.generateMediationMatrix(self.webAppDependencyMatrix)

        generationComplete = True
        for i in range(1, self.webAppDependencyMatrix.getSize()):
            for j in range(1, self.webAppDependencyMatrix.getSize()):
                if(referenceMediationMatrix[i][j] != generatedMediationMatrix[i][j]):
                    generationComplete = False
                    print("Error in generation of the compliance matrix at " + str(i) + ":" + str(j))

        self.assertTrue(generationComplete)

    def testCompleteMediation(self):
        print("""*** Test Archan 'complete mediation' / online store ***""")
        archan = Archan()
        compliant = archan.checkCompleteMediation(self.webAppDependencyMatrix)
        if(compliant):
            print("Complete Mediation is enforced")
        else:
            print("Complete Mediation is NOT enforced")
        self.assertTrue(compliant)

    def testEconomyOfMechanism(self):
        print("""*** Test Archan 'Economy of Mechanism' ***""")
        archan = Archan()
        economyOfMechanism = archan.checkEconomyOfMechanism(self.webAppDependencyMatrix)
        if(economyOfMechanism):
            print("Economy of Mechanism is enforced")
        else:
            print("Economy of Mechanism is NOT enforced")
        self.assertTrue(economyOfMechanism)

    def testLeastCommonMechanism(self):
        print("""*** Test Archan 'Least common Mechanism' ***""")
        archan = Archan()
        leastCommonMechanism = archan.checkLeastCommonMechanism(self.webAppDependencyMatrix)
        if(leastCommonMechanism):
            print("Least common Mechanism is enforced")
        else:
            print("Least common Mechanism is NOT enforced")
        self.assertTrue(leastCommonMechanism)

    def testOpenDesign(self):
        print("""*** Test Archan 'Open Design' ***""")
        archan = Archan()
        openDesign = archan.checkOpenDesign()
        if(openDesign):
            print("Open Design is enforced")
        else:
            print("Open Design is NOT enforced")
        self.assertTrue(openDesign)

    # Test Genida
    def testEconomyOfMechanismGenida(self):
        print("""*** Test Archan for Genida 'Economy of Mechanism' ***""")
        archan = Archan()
        economyOfMechanism = archan.checkEconomyOfMechanism(self.genidaDM)
        if(economyOfMechanism):
            print("Economy of Mechanism is enforced for Genida")
        else:
            print("Economy of Mechanism is NOT enforced for Genida")
        self.assertTrue(economyOfMechanism)

    def testLeastCommonMechanismGenida(self):
        print("""*** Test Archan for Genida 'Least common Mechanism' ***""")
        archan = Archan()
        leastCommonMechanism = archan.checkLeastCommonMechanism(self.genidaDM)
        if(leastCommonMechanism):
            print("Least common Mechanism is enforced for Genida")
        else:
            print("Least common Mechanism is NOT enforced for Genida")
        self.assertTrue(leastCommonMechanism)

    def testCompleteMediationGenida(self):
        print("""*** Test Archan for Genida 'complete mediation' / online store ***""")
        archan = Archan()
        compliant = archan.checkCompleteMediation(self.genidaDM)
        if(compliant):
            print("Complete Mediation is enforced for Genida")
        else:
            print("Complete Mediation is NOT enforced for Genida")
        self.assertTrue(compliant)

    def testCodeClean(self):
        archan = Archan()
        self.assertTrue(archan.checkCodeClean())
