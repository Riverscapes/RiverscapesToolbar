from os import path
from PyQt4 import QtGui
from settings import Settings
from PyQt4.QtGui import  QMenu, QTreeWidgetItem, QMessageBox, QIcon, QPixmap, QDesktopServices
from PyQt4.QtCore import Qt, QUrl

from symbology.symbology import Symbology

from qgis.utils import iface
from qgis.core import QgsProject, QgsMapLayerRegistry, QgsRasterLayer, QgsVectorLayer
from DWTabProjectsItem import ProjectTreeItem
from resources import qTreeIconStates

class DockWidgetTabProject():

    treectl = None
    widget = None

    def __init__(self, dockWidget):

        DockWidgetTabProject.treectl = dockWidget.treeProject
        DockWidgetTabProject.widget = dockWidget
        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)

        # Load the symbolizer plugins
        self.symbology = Symbology()

        # Set up some connections for app events
        self.treectl.doubleClicked.connect(self.doubleClicked)

        self.treectl.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treectl.customContextMenuRequested.connect(self.openMenu)

        dockWidget.btnLoadProject.clicked.connect(self.projectBrowserDlg)
        dockWidget.btnLoadProject.setIcon(QIcon(qTreeIconStates.OPEN))


        dockWidget.btnProjectUpload.clicked.connect(self.projectUpload)
        dockWidget.btnProjectUpload.setIcon(QIcon(qTreeIconStates.UPLOAD))


    def projectBrowserDlg(self):
        """
        Browse for a project directory
        :return: 
        """
        settings = Settings()
        filename = QtGui.QFileDialog.getExistingDirectory(self.widget, "Open a project folder", settings.getSetting('DataDir'))
        self.projectLoad(path.join(filename, "project.rs.xml"))

    def projectUpload(self):
        print "upload"


    def doubleClicked(self, index):
        """
        Tree item double clicks
        :param index: 
        :return: 
        """
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        if theData.maptype is not None:

            addEnabled = theData.maptype != "file"
            if addEnabled:
                self.addlayertomap(item)
            else:
                self.findFolder(item)

    def openMenu(self, position):
        """
        Handle the right-click contextual menu
        :param position: 
        :return: 
        """
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
        """
        Open the file in an external app
        :param rtItem: 
        :return: 
        """
        qurl = QUrl.fromLocalFile(rtItem.filepath)
        QDesktopServices.openUrl(qurl)

    def findFolder(self, rtItem):
        """
        Open the folder in finder or windows explorer
        :param rtItem: 
        :return: 
        """
        qurl = QUrl.fromLocalFile(path.dirname(rtItem.filepath))
        QDesktopServices.openUrl(qurl)


    @staticmethod
    def _addgrouptomap(sGroupName, parentGroup):
        """
        Add a hierarchical group to the layer manager
        :param sGroupName: 
        :param parentGroup: 
        :return: 
        """

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
        """
        Add a layer to the map
        :param layer: 
        :return: 
        """
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
                parentGroup = DockWidgetTabProject._addgrouptomap(aGroup, parentGroup)

        assert parentGroup, "All rasters should be nested and so parentGroup should be instantiated by now"

        # Only add the layer if it's not already in the registry
        if not QgsMapLayerRegistry.instance().mapLayersByName(nodeData.name):
            if nodeData.maptype == 'vector':
                rOutput = QgsVectorLayer(filepath, nodeData.name, "ogr")

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
        """
        Load the XML file into the tree
        :param xmlPath: 
        :return: 
        """
        if xmlPath is None or not path.isfile(xmlPath):
            msg = "..."
            q = QMessageBox(QMessageBox.Warning, "Could not find the project XML file", msg)
            q.setStandardButtons(QMessageBox.Ok)
            i = QIcon()
            i.addPixmap(QPixmap("..."), QIcon.Normal)
            q.setWindowIcon(i)
            q.exec_()
        else:
            DockWidgetTabProject.treectl.takeTopLevelItem(0)
            rootItem = ProjectTreeItem(projectXMLfile=xmlPath, treectl=DockWidgetTabProject.treectl)
            DockWidgetTabProject.treectl.expandToDepth(5)