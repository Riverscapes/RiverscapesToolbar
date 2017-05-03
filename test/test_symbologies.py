# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'info@northarrowresearch.com'
__date__ = '2016-07-12'
__copyright__ = 'Copyright 2016, NorthArrowResearch'

import unittest
import qgis

from RiverscapesToolbar.symbology import loadPlugins, symbolize

class SymbologyTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_symbology_load(self):
        """Test we can click OK."""
        loadPlugins()
        symbolize({}, "DoD")

# if __name__ == "__main__":
#     suite = unittest.makeSuite(SymbologyTest)
#     runner = unittest.TextTestRunner(verbosity=2)
#     runner.run(suite)



