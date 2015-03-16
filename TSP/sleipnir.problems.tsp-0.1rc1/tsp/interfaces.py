#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""ITSP problem Interface"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['ITSP', ]

from sleipnir.components.entrypoint import Interface


class ITSP(Interface):
    """
    TSP interface As a contract, all components that implement this
    iface MUST implement also IProblem one
    """

    @property
    def cities(self):
        """returns a list of cities(nodes) which compose TSP problem"""
        raise NotImplementedError
