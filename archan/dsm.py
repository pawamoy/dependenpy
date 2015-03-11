"""
Created on 8 janv. 2015

@author: Pierre.Parrend
"""

from archan.errors import DSMError


class DesignStructureMatrix(object):
    """Design Structure Matrix class.

    TODO: doc
    """

    # class variables
    framework = 'framework'
    app_module = 'app_module'
    core_lib = 'core_lib'
    app_lib = 'app_lib'
    broker = 'broker'
    data = 'data'

    # entities
    # dependency_matrix

    def __init__(self, categories, entities, dependency_matrix):
        """Constructor
        """
        print("TODO - DSM: check compliance with DSM definitions and uses")
        self.categories = categories
        self.entities = entities
        self.dependency_matrix = dependency_matrix
        rows = len(dependency_matrix)
        self.size = rows
        cat_nb = len(categories)
        ent_nb = len(entities)
        rows = len(dependency_matrix)
        columns = len(dependency_matrix[0])
        if cat_nb != ent_nb:
            raise DSMError(
                "Beware: nb of categories: %s; nb of entities: %s" % (
                    cat_nb, ent_nb))
        if rows != columns:
            raise DSMError(
                "Beware: nb of rows: %s; nb of columns: %s in DSM matrix" % (
                    rows, columns))
        if ent_nb != rows:
            raise DSMError(
                "Beware: nb of entities: %s; nb of rows: %s" % (ent_nb, rows))

    def set_categories(self, categories):
        self.categories = categories

    def get_categories(self):
        return self.categories

    def set_entities(self, entities):
        self.entities = entities

    def get_entities(self):
        return self.entities

    def set_dependency_matrix(self, dependency_matrix):
        self.dependency_matrix = dependency_matrix

    def get_dependency_matrix(self):
        return self.dependency_matrix

    def get_size(self):
        return self.size