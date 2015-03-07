'''
Created on 8 janv. 2015

@author: Pierre.Parrend
'''

from fr.unistra.icube_bfo.archan.errors import DSMError


class DesignStructureMatrix(object):
    '''
    classdocs
    '''

    # class variables
    framework = 'framework'
    app_module = 'app_module'
    core_lib = 'core_lib'
    app_lib = 'app_lib'
    broker = 'broker'
    data = 'data'

    # entities
    # dependencyMatrix

    def __init__(self, categories, entities, dependencyMatrix):
        '''
        Constructor
        '''
        print("TODO - DSM: check compliance with DSM definitions and uses")
        self.categories = categories
        self.entities = entities
        self.dependencyMatrix = dependencyMatrix
        rows = len(dependencyMatrix)
        self.size = rows
        catNb = len(categories)
        entNb = len(entities)
        rows = len(dependencyMatrix)
        columns = len(dependencyMatrix[0])
        if(catNb != entNb):
            raise DSMError("Beware: nb of categories: "+str(catNb) +
                           "; nb of entities: " + str(entNb))
        if(rows != columns):
            raise DSMError("Beware: nb of rows: "+str(rows) +
                           "; nb of columns: " + str(columns) +
                           "in DSM matrix")
        if(entNb != rows):
            raise DSMError("Beware: nb of entities: "+str(entNb) +
                           "; nb of rows: " + str(rows))

    def setCategories(self, categories):
        self.categories = categories

    def getCategories(self):
        return self.categories

    def setEntities(self, entities):
        self.entities = entities

    def getEntities(self):
        return self.entities

    def setDependencyMatrix(self, dependencyMatrix):
        self.dependencyMatrix = dependencyMatrix

    def getDependencyMatrix(self):
        return self.dependencyMatrix

    def getSize(self):
        return self.size