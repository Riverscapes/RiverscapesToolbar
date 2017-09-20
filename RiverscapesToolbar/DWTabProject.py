from os import path
from PyQt4 import QtGui
from settings import Settings
from PyQt4.QtGui import  QMenu, QMessageBox, QIcon, QPixmap, QDesktopServices
from PyQt4.QtCore import Qt, QUrl

from symbology.symbology import Symbology
from program import Program
from qgis.core import QgsProject, QgsMapLayerRegistry, QgsRasterLayer, QgsVectorLayer
from DWTabProjectsItem import ProjectTreeItem

from resources import qTreeIconStates
from lib.s3.operations import S3Operation
from AddQueueDialog import AddQueueDialog
from project import Project


class DockWidgetTabProject():

    treectl = None
    dockwidget = None
    project = None

    layerlibrary = []

    def __init__(self, dockWidget):

        DockWidgetTabProject.treectl = dockWidget.treeProject
        DockWidgetTabProject.dockwidget = dockWidget
        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)

        # This will hopefully allow custom triggering of layer re-ordering
        # QgsMapLayerRegistry.instance().legendLayersAdded.connect(self.rearrangeLayers)

        # Load the symbolizer plugins
        self.symbology = Symbology()

        # Set up some connections for app events
        self.treectl.doubleClicked.connect(self.doubleClicked)

        self.treectl.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treectl.customContextMenuRequested.connect(self.openMenu)

        dockWidget.btnLoadProject.clicked.connect(self.projectBrowserDlg)
        dockWidget.btnLoadProject.setIcon(QIcon(qTreeIconStates.OPEN))

        dockWidget.btnProjectUpload.clicked.connect(self.projectUpload)
        dockWidget.btnProjectUpload.setIcon(QIcon(qTreeIconStates.UPLOADBTN))


    def projectBrowserDlg(self):
        """
        Browse for a project directory
        :return: 
        """
        settings = Settings()
        filename = QtGui.QFileDialog.getExistingDirectory(self.dockwidget, "Open a project folder", settings.getSetting('DataDir'))
        if filename is not None and filename != "":
            self.projectLoad(path.join(filename, program.ProjectFile), outside=True)

    def projectUpload(self):
        dialog = AddQueueDialog(S3Operation.Direction.UP, DockWidgetTabProject.project)
        if dialog.exec_():
            self.dockwidget.TabDownload.addToQueue(dialog.qItem)


    # @staticmethod
    # def rearrangeLayers(layers):
    #     print "hello"
    #     # order = iface.layerTreeCanvasBridge().customLayerOrder()
    #     # for layer in layers:  # How many layers we need to move
    #     #     order.insert(0, order.pop())  # Last layer to first position
    #     # iface.layerTreeCanvasBridge().setCustomLayerOrder(order)

    def doubleClicked(self, index):
        """
        Tree item double clicks
        :param index: 
        :return: 
        """
        itemind = self.treectl.selectedIndexes()[0]
        theData = itemind.data(Qt.UserRole)

        if theData.maptype is not None:

            addEnabled = theData.maptype != "file"
            if addEnabled:
                self.addlayertomap(itemind)
            else:
                self.externalOpen(theData)

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
            findFolderReceiver = lambda item=theData: self.findFolder(theData)
            externalOpenReceiver = lambda item=theData: self.externalOpen(theData)

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


    def openProject(self, project):
        localpath = path.join("/".join(project.pathArr))
        # Switch to the project tab
        self.dockwidget.TabProject.projectLoad(localpath)
        self.dockwidget.tabWidget.setCurrentIndex(self.dockwidget.PROJECT_TAB)

    @staticmethod
    def _addgrouptomap(sGroupName, sGroupOrder, parentGroup):
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
            thisGroup = parentGroup.insertGroup(sGroupOrder, sGroupName)

        return thisGroup

    def addlayertomap(self, qindex):
        """
        Add a layer to the map
        :param layer: 
        :return: 
        """
        # Loop over all the parent group layers for this raster
        # ensuring they are in the tree in correct, nested order
        nodeData = qindex.data(Qt.UserRole)
        symbology = nodeData.symbology
        filepath = nodeData.filepath

        # DEBUG
        item = DockWidgetTabProject.treectl.itemFromIndex(qindex)
        order = item.parent().indexOfChild(item)

        print "ADDING TO MAP::", nodeData.filepath
        # Loop over all the parent group layers for this raster
        # ensuring they are in the tree in correct, nested order
        parentGroup = None
        if len(filepath) > 0:
            for aGroup in nodeData.getTreeAncestry():
                # aGroup comes back as a tuple (name, order)
                parentGroup = DockWidgetTabProject._addgrouptomap(aGroup[0], aGroup[1], parentGroup)

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
            parentGroup.insertLayer(order, rOutput)

            # Symbolize this layer
            Symbology().symbolize(rOutput, symbology)

        # if the layer already exists trigger a refresh
        else:
            print "REFRESH"
            QgsMapLayerRegistry.instance().mapLayersByName(nodeData.name)[0].triggerRepaint()

    @staticmethod
    def projectLoad(absProjPath, outside=False):
        """
        Load the XML file into the tree
        :param xmlPath: 
        :return: 
        """

        DockWidgetTabProject.project = Project(absProjPath, outside=outside)
        DockWidgetTabProject.project.load()

        if DockWidgetTabProject.project is None or not path.isfile(DockWidgetTabProject.project.absProjectFile):
            msg = "Could not find a valid '{}' file at that location".format(program.ProjectFile)
            q = QMessageBox(QMessageBox.Warning, "Could not find the project XML file", msg)
            q.setStandardButtons(QMessageBox.Ok)
            i = QIcon()
            i.addPixmap(QPixmap("..."), QIcon.Normal)
            q.setWindowIcon(i)
            q.exec_()
        else:
            DockWidgetTabProject.treectl.takeTopLevelItem(0)
            rootItem = ProjectTreeItem(dwtab=DockWidgetTabProject)