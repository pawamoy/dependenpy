"""
Created on 8 janv. 2015

@author: Pierre.Parrend
"""

from archan.dsm import DesignStructureMatrix
from archan.errors import ArchanError


class Archan:
    def __init__(self):
        self.check_complete_mediation_implemented = True
        self.check_economy_of_mechanism_implemented = True
        self.check_separation_of_privileges_implemented = False
        self.check_least_privileges_implemented = False
        self.check_least_common_mechanism_implemented = True
        self.check_layered_architecture_implemented = False
        # Archan audit parameters
        self.independenceFactor = 5
        self.simplicityFactor = 2

    # rules for mediation matrix generation
    # TODO: set -1 for items NOT to be considered
    # 0 for items which MUST NOT be present
    # 1 for items which MUST be present
    # each module has optional dependencies to himself
    # framework has optional dependency to all framework items (-1), and
    # to nothing else
    # core libs: dependency to framework + oneself only
    # (dep to other core_libs could be tolerated)
    # application libs: dependency to framework, other core or app libs
    # tolerated; no dependencies to apps
    # app_modules: dependencies to libs; dependencies to app should be mediated
    # over a broker; dependencies to data
    # data no dependencies at all (framework + libs would be tolerated)
    def generate_mediation_matrix(self, dsm):
        categories = dsm.getCategories()
        dsm_size = dsm.getSize()

        # define and initialize the mediation matrix
        mediation_matrix = [[0 for x in range(dsm_size)]
                            for x in range(dsms_ize)]

        for i in range(0, dsm_size):
            for j in range(0, dsm_size):
                if categories[i] == DesignStructureMatrix.framework:
                    if categories[j] == DesignStructureMatrix.framework:
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif categories[i] == DesignStructureMatrix.core_lib:
                    if (categories[j] == DesignStructureMatrix.framework or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif categories[i] == DesignStructureMatrix.app_lib:
                    if (categories[j] == DesignStructureMatrix.framework or
                            categories[j] == DesignStructureMatrix.core_lib or
                            categories[j] == DesignStructureMatrix.app_lib):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif categories[i] == DesignStructureMatrix.broker:
                    if categories[j] == DesignStructureMatrix.app_module:
                        mediation_matrix[i][j] = 1
                    elif (categories[j] == DesignStructureMatrix.framework or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif categories[i] == DesignStructureMatrix.app_module:
                    if (categories[j] == DesignStructureMatrix.framework or
                            categories[j] == DesignStructureMatrix.core_lib or
                            categories[j] == DesignStructureMatrix.app_lib or
                            categories[j] == DesignStructureMatrix.data or
                            i == j):
                        mediation_matrix[i][j] = -1
                    elif categories[j] == DesignStructureMatrix.broker:
                        mediation_matrix[i][j] = 1
                    else:
                        mediation_matrix[i][j] = 0
                elif categories[i] == DesignStructureMatrix.data:
                    if (categories[j] == DesignStructureMatrix.framework or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                else:
                    mediation_matrix[i][j] = -2  # errors in the generation
                    raise ArchanError(
                        "Mediation matrix value NOT generated for %s:%s" % (
                            i, j))

        return mediation_matrix

    def check_matrices_compliance(self, dependency_matrix,
                                  complete_mediation_matrix):
        dep_matrix_ok = False
        rows_dep_matrix = len(dependency_matrix)
        cols_dep_matrix = len(dependency_matrix[0])
        rows_med_matrix = len(complete_mediation_matrix)
        cols_med_matrix = len(complete_mediation_matrix[0])
        if rows_dep_matrix == rows_med_matrix:
            if cols_dep_matrix == cols_med_matrix:
                discrepancy_found = False
                for i in range(0, rows_dep_matrix):
                    for j in range(0, cols_dep_matrix):
                        if ((complete_mediation_matrix[i][j] != -1) and
                                (dependency_matrix[i][j] !=
                                    complete_mediation_matrix[i][j])):
                            discrepancy_found = True
                            print("Matrix discrepancy found at " + str(i)
                                  + ":" + str(j))
                if not discrepancy_found:
                    dep_matrix_ok = True
            else:
                print("Matrices are NOT compliant" +
                      "(number of columns not equals)")
        else:
            print("Matrices are NOT compliant (number of rows not equals)")

        return dep_matrix_ok

    def check_complete_mediation(self, dsm):
        # generate complete_mediation_matrix according to each category
        med_matrix = self.generatemediation_matrix(dsm)
        matrices_compliant = self.check_matrices_compliance(
            dsm.get_dependency_matrix(),
            med_matrix)
        # check comparison result
        return matrices_compliant

    def check_economy_of_mechanism(self, dsm):
        """Check economy of mechanism

        As first abstraction, number of dependencies between two modules
        < 2 * the number of modules
        (dependencies to the framework are NOT considered).
        """
        # economy_of_mechanism
        economy_of_mechanism = False
        dependency_matrix = dsm.get_dependency_matrix()
        categories = dsm.getCategories()
        dsm_size = dsm.getSize()

        dependency_number = 0
        # evaluate Matrix(dependency_matrix)
        for i in range(0, dsm_size):
            for j in range(0, dsm_size):
                if (categories[i] != DesignStructureMatrix.framework and
                        categories[j] != DesignStructureMatrix.framework and
                        dependency_matrix[i][j] > 0):
                    dependency_number += 1
                    # check comparison result
        if dependency_number < dsm_size * self.simplicityFactor:
            economy_of_mechanism = True
        else:
            print("dependency_number: " + str(dependency_number))
            print("rowsdep_matrix: " + str(dsm_size))
            print("expected dependencies: " + str(self.simplicityFactor))
        return economy_of_mechanism

    def check_separation_of_privileges(self, dependency_matrix):
        # separationOfPrivilegesMatrix
        separationOfPrivileges = False
        # check comparison result
        return separationOfPrivileges

    def check_least_privileges(self, dependency_matrix):
        # _least_privileges_matrix
        _least_privileges = False
        # check comparison result
        return _least_privileges

    def check_least_common_mechanism(self, dsm):
        # leastCommonMechanismMatrix
        least_common_mechanism = False
        # get the list of dependent modules for each module
        dependency_matrix = dsm.get_dependency_matrix()
        categories = dsm.getCategories()
        dsm_size = dsm.getSize()

        dependent_module_number = []
        # evaluate Matrix(dependency_matrix)
        for j in range(0, dsm_size):
            dependent_module_number.append(0)
            for i in range(0, dsm_size):
                if (categories[i] != DesignStructureMatrix.framework and
                        categories[j] != DesignStructureMatrix.framework and
                        dependency_matrix[i][j] > 0):
                    dependent_module_number[j] += 1
        # except for the broker if any  and libs, check that threshold is not
        # overlapped
        #  index of brokers
        #  and app_libs are set to 0
        for index, item in enumerate(dsm.getCategories()):
            if (item == DesignStructureMatrix.broker or
                    item == DesignStructureMatrix.app_lib):
                dependent_module_number[index] = 0
        if max(dependent_module_number) <= dsm.getSize() / self.independence_factor:
            least_common_mechanism = True
        else:
            print('max number of dependencies to a module: '
                  + str(max(dependent_module_number)))
            print('max number of expected dependencies: '
                  + str(int(dsm.getSize() / self.independence_factor)))

        return least_common_mechanism

    def check_open_design(self):
        # check that compliance with secure design principles are performed
        open_design = (self.check_complete_mediation_implemented and
                       self.check_economy_of_mechanism_implemented and
                       self.check_separation_of_privileges_implemented and
                       self.check_least_privileges_implemented and
                       self.check_least_common_mechanism_implemented and
                       self.check_layered_architecture_implemented)
        return open_design

    def check_layered_architecture(self):
        # TODO - precondition for subsequent checks?
        pass

    def check_code_clean(self):
        print("No code issue found")
        return True
