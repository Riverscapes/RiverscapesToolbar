# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Riverscapes Toolbar
                                 A QGIS plugin
 View Riverscapes Toolbar Files
                             -------------------
        begin                : 2016-07-12
        copyright            : (C) 2016 by NorthArrowResearch
        email                : info@northarrowresearch.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

######################### REMOTE DEBUG #########################
# To activate remote debugging set DEBUG_PLUGIN=RiverscapesToolbar as a QGIS
# Environment variable in Preferences -> System -> Environment
import os
import logging
DEBUG = False

from RiverscapesToolbar.lib import debug
if 'DEBUG_PLUGIN' in os.environ and os.environ['DEBUG_PLUGIN'] == "RiverscapesToolbar":
    debug.InitDebug()
    DEBUG = True
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
######################### /REMOTE DEBUG #########################


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ToolbarViewer class from file ToolbarViewer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .toolbar_viewer import RiverscapesToolbarViewer
    return RiverscapesToolbarViewer(iface)
