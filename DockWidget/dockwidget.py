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
from settings_dialog import SettingsDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'DockWidget.ui'))

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

    self.tree_widget.customContextMenuRequested.connect(self._contextMenu)


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

    def _contextMenu(self, point):
        """
        Context Menu (right click on the treeWidget)
        """

        item = self.tree_widget.itemAt(point)
        name_clicked = self._get_tag_from_item(item)

        def add_tag():
            dialog = QtGui.QInputDialog()
            dialog.setTextValue(name_clicked)
            if name_clicked != "":
                proposition = name_clicked + '/'
            else:
                proposition = name_clicked
            (tag, confirm) = dialog.getText(QtGui.QWidget(), \
                                            "new tag", \
                                            "enter tag name", \
                                            0, \
                                            proposition)
            tag = str(tag)
            if tag.endswith("/"):
                raise ValueError("""tag should not end with /""")
            if confirm and tag != "":
                try:
                    Tag.objects.get(name=tag)
                except Tag.DoesNotExist:
                    Tag.objects.create(name=tag)
                    self.add_item(tag)
                    self.select(tag)
                    model_monitor.tag_added.emit()
                else:
                    box = QtGui.QMessageBox()
                    box.setText("tag " + tag + " allready exists")
                    box.exec_()

        def remove_tag(dummy, name=name_clicked):
            dial = QtGui.QMessageBox()
            dial.setText("Delete tag '" + name + "': are you sure ?")
            dial.setInformativeText("Tag will be removed from all referenced curves...")
            dial.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
            dial.setDefaultButton(QtGui.QMessageBox.Ok);
            if dial.exec_():
                tag = Tag.objects.get(name=name)
                tag.delete()
                model_monitor.tag_deletted.emit()
                self.refresh()

        def rename(dummy, name=name_clicked):
            dialog = QtGui.QInputDialog()
            dialog.setTextValue(name_clicked)
            proposition = name_clicked
            (tag, confirm) = dialog.getText(QtGui.QWidget(), \
                                            "rename tag", \
                                            "enter tag name", \
                                            0, \
                                            proposition)
            if confirm:
                new_name = str(tag)
                tag = Tag.objects.get(name=name)
                tag.name = new_name
                tag.save()
                self.refresh()

        menu = QtGui.QMenu(self)
        action_add_tag = QtGui.QAction("add tag...", self)
        action_add_tag.triggered.connect(add_tag)
        menu.addAction(action_add_tag)

        action_rename_tag = QtGui.QAction("rename tag", self)
        action_rename_tag.triggered.connect(rename)
        menu.addAction(action_rename_tag)

        action_remove_tag = QtGui.QAction("remove tag", self)
        action_remove_tag.triggered.connect(remove_tag)
        menu.addAction(action_remove_tag)

        action_refresh_list = QtGui.QAction("refresh list", self)
        action_refresh_list.triggered.connect(self.refresh)
        menu.addAction(action_refresh_list)

        self._exec_menu_at_right_place(menu, point)
