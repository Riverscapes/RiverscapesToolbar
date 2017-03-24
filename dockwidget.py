# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RiverscapesToolbarDockWidget
                                 A QGIS plugin
 View RiverscapesToolbarDockWidget Files
                             -------------------
        begin                : 2016-07-12
        git sha              : $Format:%H$
        copyright            : (C) 2016 by NorthArrowResearch
        email                : info@northarrowresearch.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui
import PyQt4.uic as uic
from PyQt4.QtCore import pyqtSignal
from lib.projects import ProjectXML
import DockWidgetTabs
from SettingsDialog import SettingsDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dockwidget.ui'))

class RiverscapesToolbarDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(RiverscapesToolbarDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.btnLoad.clicked.connect(self.raster_file_browser)
        self.btnSettings.clicked.connect(self.settingsLoad)

        # Set the ability to have a context menu
        # treeView->setContextMenuPolicy(Qt::CustomContextMenu);
        # self.tree_widget.customContextMenuRequested.connect(DockWidgetTabs.Download.ContextMenu)


    def settingsLoad(self):
        dialog = SettingsDialog()
        dialog.exec_()

    def raster_file_browser(self):
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Open XML file", "", "XML File (*.xml);;GCD File (*.gcd);;All files (*)")
        self.xmlLocation.setText(filename)
        self.projectXML = ProjectXML(filename, self.treeView)
        self.recalc_state()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def recalc_state(self):
        print "recalc state"

