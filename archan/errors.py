'''
Created on 17 fevr. 2015

@author: Pierre.Parrend
'''


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class DSMError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

class ArchanError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
