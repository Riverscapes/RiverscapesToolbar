from os import path
from PyQt4 import QtGui
from settings import Settings
from PyQt4.QtGui import  QMenu, QTreeWidgetItem, QMessageBox, QIcon, QPixmap, QDesktopServices
from PyQt4.QtCore import Qt, QUrl

from symbology.symbology import Symbology

from qgis.utils import iface
from qgis.core import QgsProject, QgsMapLayerRegistry, QgsRasterLayer, QgsVectorLayer
from lib.projects import ProjectTreeItem


class DockWidgetTabProject():

    treectl = None

    def __init__(self, dockWidget):
        print "init"
        DockWidgetTabProject.treectl = dockWidget.treeProject
        self.widget = dockWidget
        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)

        # Load the symbolizer plugins
        self.symbology = Symbology()

        # Set up some connections for app events
        self.treectl.doubleClicked.connect(self.doubleClicked)

        self.treectl.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treectl.customContextMenuRequested.connect(self.openMenu)

        dockWidget.btnLoadProject.clicked.connect(self.projectBrowserDlg)
        dockWidget.btnDEBUG.clicked.connect(self.loadDebug)


    def projectBrowserDlg(self):
        settings = Settings()
        filename = QtGui.QFileDialog.getExistingDirectory(self.widget, "Open a project", settings.getSetting('DataDir'))
        self.projectLoad(path.join(filename, "project.rs.xml"))

    def loadDebug(self):
        """
        Quick and dirty hardcoded project loader so I can start work
        :return:
        """
        # Start by clearing out the previous children (this is a forced or first refresh)
        QTreeWidgetItem(DockWidgetTabProject.treectl).takeChildren()
        self.projectLoad('/Users/work/Projects/Riverscapes/Data/CRB/MiddleForkJohnDay/Network/VBET/project.rs.xml')

    def doubleClicked(self, index):
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        if theData.maptype is not None:

            addEnabled = theData.maptype != "file"
            if addEnabled:
                self.addlayertomap(item)
            else:
                self.findFolder(item)

    def openMenu(self, position):
        """ Handle the contextual menu """
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        menu = QMenu()

        if theData.maptype is not None:

            addReceiver = lambda item=item: self.addlayertomap(item)
            findFolderReceiver = lambda item=theData: self.findFolder(item)
            externalOpenReceiver = lambda item=theData: self.externalOpen(item)

            findAction = menu.addAction("Open Containing Folder", findFolderReceiver)

            addEnabled = theData.maptype != "file"

            if addEnabled:
                addAction = menu.addAction("Add to Map", addReceiver)
            else:
                openAction = menu.addAction("Open File", externalOpenReceiver)

        menu.exec_(self.treectl.mapToGlobal(position))

    def externalOpen(self, rtItem):
        qurl = QUrl.fromLocalFile(rtItem.filepath)
        QDesktopServices.openUrl(qurl)

    def findFolder(self, rtItem):
        qurl = QUrl.fromLocalFile(path.dirname(rtItem.filepath))
        QDesktopServices.openUrl(qurl)


    @staticmethod
    def addgrouptomap(sGroupName, parentGroup):

        # If no parent group specified then the parent is the ToC tree root
        if not parentGroup:
            parentGroup = QgsProject.instance().layerTreeRoot()

        # Attempt to find the specified group in the parent
        thisGroup = parentGroup.findGroup(sGroupName)
        if not thisGroup:
            thisGroup = parentGroup.insertGroup(0, sGroupName)

        return thisGroup


    @staticmethod
    def addlayertomap(layer):

        # Loop over all the parent group layers for this raster
        # ensuring they are in the tree in correct, nested order
        nodeData = layer.data(Qt.UserRole)
        symbology = nodeData.symbology
        filepath = nodeData.filepath

        print "ADDING TO MAP::", nodeData.filepath
        # Loop over all the parent group layers for this raster
        # ensuring they are in the tree in correct, nested order
        parentGroup = None
        if len(filepath) > 0:
            for aGroup in nodeData.getTreeAncestry():
                parentGroup = DockWidgetTabProject.addgrouptomap(aGroup, parentGroup)

        assert parentGroup, "All rasters should be nested and so parentGroup should be instantiated by now"

        # Only add the layer if it's not already in the registry
        if not QgsMapLayerRegistry.instance().mapLayersByName(nodeData.name):
            if nodeData.maptype == 'vector':
                rOutput = QgsVectorLayer(filepath, nodeData.name, "ogr")

                # legend = iface.legendInterface()
                # legend.setLayerExpanded(rOutput, False)

            elif nodeData.maptype == 'raster':
                # Raster
                rOutput = QgsRasterLayer(filepath, nodeData.name)


            elif nodeData.maptype == 'tilelayer':
                print "WARNING:::  not implemented yet"

            QgsMapLayerRegistry.instance().addMapLayer(rOutput, False)
            parentGroup.addLayer(rOutput)

            # Symbolize this layer
            Symbology().symbolize(rOutput, symbology)

        # if the layer already exists trigger a refresh
        else:
            print "REFRESH"
            QgsMapLayerRegistry.instance().mapLayersByName(nodeData.name)[0].triggerRepaint()

    @staticmethod
    def projectLoad(xmlPath):
        """ Constructor """
        if xmlPath is None or not path.isfile(xmlPath):
            msg = "..."
            q = QMessageBox(QMessageBox.Warning, "Could not find the project XML file", msg)
            q.setStandardButtons(QMessageBox.Ok)
            i = QIcon()
            i.addPixmap(QPixmap("..."), QIcon.Normal)
            q.setWindowIcon(i)
            q.exec_()
        else:
            rootItem = ProjectTreeItem(projectXMLfile=xmlPath, treectl=DockWidgetTabProject.treectl)
            DockWidgetTabProject.treectl.expandToDepth(5)