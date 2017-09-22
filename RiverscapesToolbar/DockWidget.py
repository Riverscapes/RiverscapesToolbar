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
from SettingsDialog import SettingsDialog
from PyQt4.QtGui import QIcon

from DWTabRepository import DockWidgetTabRepository
from DWTabDownload import DockWidgetTabDownload
from DWTabProject import DockWidgetTabProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../DockWidget.ui'))

class RiverscapesToolbarDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    showMessageBox = pyqtSignal(str, str, str, object)

    REPO_TAB = 0
    PROJECT_TAB = 1
    DOWNLOAD_TAB = 2

    def __init__(self, parent=None):
        """Constructor."""

        super(RiverscapesToolbarDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Connect up our top-level components that aren't in tabs
        # self.btnLoad.clicked.connect(self.raster_file_browser)
        self.btnSettings.clicked.connect(self.settingsLoad)
        self.tabWidget.setCurrentIndex(self.REPO_TAB)

        # For asynchronous tasks we need to only ever call the okdlg on the
        # Main thread
        self.showMessageBox.connect(self.okDlg)

        # The code that runs our tabs lives in a different class
        self.TabRepo = DockWidgetTabRepository(self)
        self.TabDownload = DockWidgetTabDownload(self)
        self.TabProject = DockWidgetTabProject(self)

    def settingsLoad(self):
        dialog = SettingsDialog()
        dialog.exec_()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def recalc_state(self):
        return
        # print "recalc state"

    @staticmethod
    def okDlg(txt, infoText="", detailsTxt=None, icon=QtGui.QMessageBox.Information):
        """
        Call it like this:
            self.okDlg("ERROR:", infoText=str(e), detailsTxt=detailstxt, icon=QtGui.QMessageBox.Critical)
        :param self:
        :param txt:
        :param infoText:
        :param detailsTxt:
        :param icon:
        :return:
        """

        # Just a helper box to display an OK dialog prompt.
        msg = QtGui.QMessageBox()
        msg.setIcon(icon)

        msg.setText(txt)
        msg.setInformativeText(infoText)
        msg.setWindowTitle("Riverscapes Toolbar")
        if detailsTxt is not None:
            msg.setDetailedText(detailsTxt)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)

        # This is a hack to be able to resize the box
        horizontal_spacer = QtGui.QSpacerItem(500, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        layout = msg.layout()
        layout.addItem(horizontal_spacer, layout.rowCount(), 0, 1, layout.columnCount())

        msg.exec_()
