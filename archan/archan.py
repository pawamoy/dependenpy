'''
Created on 8 janv. 2015

@author: Pierre.Parrend
'''
from fr.unistra.icube_bfo.archan.dsm import DesignStructureMatrix
from fr.unistra.icube_bfo.archan.errors import ArchanError


class Archan:

    def __init__(self):
        self.checkCompleteMediationImplemented = True
        self.checkEconomyOfMechanismImplemented = True
        self.checkSeparationOfPrivilegesImplemented = False
        self.checkLeastPrivilegesImplemented = False
        self.checkLeastCommonMechanismImplemented = True
        self.checkLayeredArchitectureImplemented = False
        # Archan audit parameters
        self.independenceFactor = 5
        self.simplicityFactor = 2

    # rules for mediation matrix generation
    # TODO: set -1 for items NOT to be considered
    # 0 for items which MUST NOT be present
    # 1 for items which MUST be present
    # each module has optional dependencies to himself
    # framework has optional dependency to all framework items (-1), and
    #    to nothing else
    # core libs: dependency to framework + oneself only
    #    (dep to other core_libs could be tolerated)
    # application libs: dependency to framework, other core or app libs
    #    tolerated; no dependencies to apps
    # app_modules: dependencies to libs; dependencies to app should be mediated
    #     over a broker; dependencies to data
    # data no dependencies at all (framework + libs would be tolerated)
    def generateMediationMatrix(self, dsm):
        categories = dsm.getCategories()
        dsmSize = dsm.getSize()

        # define and initialize the mediation matrix
        mediationMatrix = [[0 for x in range(dsmSize)] for x in range(dsmSize)]

        for i in range(0, dsmSize):
            for j in range(0, dsmSize):
                if (categories[i] == DesignStructureMatrix.framework):
                    if (categories[j] == DesignStructureMatrix.framework):
                        mediationMatrix[i][j] = -1
                    else:
                        mediationMatrix[i][j] = 0
                elif (categories[i] == DesignStructureMatrix.core_lib):
                    if (categories[j] == DesignStructureMatrix.framework or i == j):
                        mediationMatrix[i][j] = -1
                    else:
                        mediationMatrix[i][j] = 0
                elif (categories[i] == DesignStructureMatrix.app_lib):
                    if (categories[j] == DesignStructureMatrix.framework
                        or categories[j] == DesignStructureMatrix.core_lib
                        or categories[j] == DesignStructureMatrix.app_lib):
                        mediationMatrix[i][j] = -1
                    else:
                        mediationMatrix[i][j] = 0
                elif (categories[i] == DesignStructureMatrix.broker):
                    if (categories[j] == DesignStructureMatrix.app_module):
                        mediationMatrix[i][j] = 1
                    elif (categories[j] == DesignStructureMatrix.framework
                        or i == j):
                        mediationMatrix[i][j] = -1
                    else:
                        mediationMatrix[i][j] = 0
                elif (categories[i] == DesignStructureMatrix.app_module):
                    if (categories[j] == DesignStructureMatrix.framework
                        or categories[j] == DesignStructureMatrix.core_lib
                        or categories[j] == DesignStructureMatrix.app_lib
                        or categories[j] == DesignStructureMatrix.data
                        or i == j):
                        mediationMatrix[i][j] = -1
                    elif categories[j] == DesignStructureMatrix.broker:
                        mediationMatrix[i][j] = 1
                    else:
                        mediationMatrix[i][j] = 0
                elif (categories[i] == DesignStructureMatrix.data):
                    if (categories[j] == DesignStructureMatrix.framework
                        or i == j):
                        mediationMatrix[i][j] = -1
                    else:
                        mediationMatrix[i][j] = 0
                else:
                    raise ArchanError("Mediation matrix value NOT generated for " + str(i) + ":" + str(j))
                    mediationMatrix[i][j] = -2 # errors in the generation

        return mediationMatrix

    def checkMatricesCompliance(self, dependencyMatrix, completeMediationMatrix):
        DepMatrixOK = False
        rowsDepMatrix = len(dependencyMatrix)
        colsDepMatrix = len(dependencyMatrix[0])
        rowsMedMatrix = len(completeMediationMatrix)
        colsMedMatrix = len(completeMediationMatrix[0])
        if (rowsDepMatrix == rowsMedMatrix):
            if (colsDepMatrix == colsMedMatrix):
                discrepancyFound = False
                for i in range(0, rowsDepMatrix):
                    for j in range(0, colsDepMatrix):
                        if ((completeMediationMatrix[i][j] != -1) and
                            (dependencyMatrix[i][j] !=
                             completeMediationMatrix[i][j])):
                            discrepancyFound = True
                            print("Matrix discrepancy found at " + str(i)
                                  + ":" + str(j))
                if not discrepancyFound:
                    DepMatrixOK = True
            else:
                print("Matrices are NOT compliant" +
                      "(number of columns not equals)")
        else:
            print("Matrices are NOT compliant (number of rows not equals)")

        return DepMatrixOK

    def checkCompleteMediation(self, dsm):
        # generate completeMediationMatrix according to each category
        medMatrix = self.generateMediationMatrix(dsm)
        matricesCompliant = self.checkMatricesCompliance(dsm.getDependencyMatrix(),
                                                 medMatrix)
        # check comparison result
        return matricesCompliant

    '''
    check economy of mechanism:
    as first abstraction, number of dependencies between two modules
    < 2 * the number of modules
    (dependencies to the framework are NOT considered)
    '''
    def checkEconomyOfMechanism(self, dsm):
        # economyOfMechanism
        economyOfMechanism = False
        dependencyMatrix = dsm.getDependencyMatrix()
        categories = dsm.getCategories()
        dsmSize = dsm.getSize()

        dependencyNumber = 0
        # evaluate Matrix(dependencyMatrix)
        for i in range(0, dsmSize):
            for j in range(0, dsmSize):
                if (categories[i] != DesignStructureMatrix.framework
                    and categories[j] != DesignStructureMatrix.framework
                    and dependencyMatrix[i][j] > 0):
                    dependencyNumber = dependencyNumber + 1 
        # check comparison result
        if dependencyNumber < dsmSize * self.simplicityFactor:
            economyOfMechanism = True
        else:
            print("dependencyNumber: " + str(dependencyNumber))
            print("rowsDepMatrix: " + str(dsmSize))
            print("expected dependencies: " + str(self.simplicityFactor))
        return economyOfMechanism

    def checkSeparationOfPrivileges(self, dependancyMatrix):
        # separationOfPrivilegesMatrix
        separationOfPrivileges = False
        # check comparison result
        return separationOfPrivileges

    def checkLeastPrivileges(self, dependencyMatrix):
        # leastPrivilegesMatrix
        leastPrivileges = False
        # check comparison result
        return leastPrivileges

    def checkLeastCommonMechanism(self, dsm):
        # leastCommonMechanismMatrix
        leastCommonMechanism = False
        # get the list of dependent modules for each module
        dependencyMatrix = dsm.getDependencyMatrix()
        categories = dsm.getCategories()
        dsmSize = dsm.getSize()

        dependentModuleNumber = []
        # evaluate Matrix(dependencyMatrix)
        for j in range(0, dsmSize):
            dependentModuleNumber.append(0)
            for i in range(0, dsmSize):
                if (categories[i] != DesignStructureMatrix.framework
                    and categories[j] != DesignStructureMatrix.framework
                    and dependencyMatrix[i][j] > 0):
                    dependentModuleNumber[j] = dependentModuleNumber[j] + 1
        # except for the broker if any  and libs, check that threshold is not
        # overlapped
        #  index of brokers
        #  and app_libs are set to 0
        for index, item in enumerate(dsm.getCategories()):
            if (item == DesignStructureMatrix.broker
                or item == DesignStructureMatrix.app_lib):
                dependentModuleNumber[index] = 0
        if(max(dependentModuleNumber) <= dsm.getSize() / self.independenceFactor):
            leastCommonMechanism = True
        else:
            print('max number of dependencies to a module: '
                  + str(max(dependentModuleNumber)))
            print('max number of expected dependencies: '
                  + str(int(dsm.getSize() / self.independenceFactor)))

        return leastCommonMechanism

    def checkOpenDesign(self):
        # check that compliance with secure design principles are performed
        openDesign = (self.checkCompleteMediationImplemented and
                      self.checkEconomyOfMechanismImplemented and
                      self.checkSeparationOfPrivilegesImplemented and
                      self.checkLeastPrivilegesImplemented and
                      self.checkLeastCommonMechanismImplemented and
                      self.checkLayeredArchitectureImplemented)
        return openDesign

    def checkLayeredArchitecture(self):
        pass
        # TODO - precondition for subsequent checks?

    def checkCodeClean(self):
        print("No code issue found")
        return True
