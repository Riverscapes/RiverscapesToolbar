import logging
from lib.program import ProgramXML
from lib.s3.walkers import s3GetFolderList, s3Exists, s3HeadData
import datetime
from settings import Settings
from PyQt4.QtGui import QStandardItem, QMenu, QMessageBox, QStandardItemModel, QBrush, QColor, QDesktopServices
from PyQt4.QtCore import Qt, QUrl
from StringIO import StringIO
from os import path
from lib.toc_management import *
from PopupDialog import okDlg

class DockWidgetTabRepository():

    def __init__(self, dockWidget):
        # used to be:
        # def __init__(self, xmlPath, treeControl, parent=None):
        # Connect up our buttons to functions
        self.tree = dockWidget.treeRepository
        self.tree.alternatingRowColors()
        self.dockwidget = dockWidget
        dockWidget.btnRefresh.clicked.connect(self.btn_refresh)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)

    def btn_refresh(self):
        """
        Refresh the main dialog
        :return:
        """
        print "clicked"
        self.dockwidget.btnRefresh.setText("Loading...")
        self.dockwidget.btnRefresh.setEnabled(False)
        settings = Settings()

        # Set a static variable for this class
        RepoTreeItem.program = ProgramXML(settings.getSetting('ProgramXMLUrl'))
        RepoTreeItem.localdir = settings.getSetting('DataDir')

        if RepoTreeItem.program.DOM is None:
            okDlg("ERROR:", infoText="Error downloading the program XML file", detailsTxt= "Error downloading the program XML file", icon=QMessageBox.Critical)
        else:
            model = QStandardItemModel()
            self.tree.setModel(model)

            # Set up the first domino for the recursion
            rootItem = RepoTreeItem(RepoTreeItem.program.Hierarchy, model, loadlevels=4)
            model.appendRow(rootItem.qStdItem)

            self.tree.expandToDepth(2)
        self.dockwidget.btnRefresh.setEnabled(True)
        self.dockwidget.btnRefresh.setText("Refresh")


    # ------------------------------------------------
    # Convenience Functions
    # ------------------------------------------------
    def item_doubleClicked(self, index):
        item = self.tree.selectedIndexes()[0]
        # self.openProject(item.model().itemFromIndex(index))
        # menu.exec_(self.tree.viewport().mapToGlobal(position))

    def openMenu(self, pt):
        """ Handle the contextual menu """
        item = self.tree.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        if (theData.type=="product"):
            menu = QMenu()
            openReciever = lambda item=theData: self.openProject(item)
            downloadReciever = lambda item=theData: self.addProjectToDownloadQueue(item)
            uploadReciever = lambda item=theData: self.addProjectToUploadQueue(item)
            findFolderReciever = lambda item=theData: self.findFolder(item)

            openAction = menu.addAction("Open Project", openReciever)
            menu.addSeparator()
            downAction = menu.addAction("Download Project", downloadReciever)
            uploAction = menu.addAction("Upload Project", uploadReciever)
            menu.addSeparator()
            findAction = menu.addAction("Find Folder", findFolderReciever)
            menu.exec_(self.tree.mapToGlobal(pt))

    def addProjectToDownloadQueue(self, rtItem):
        print "Adding to download Queue: " + '/'.join(rtItem.path)

    def addProjectToUploadQueue(self, rtItem):
        print "Adding to Upload Queue: " + '/'.join(rtItem.path)

    def findFolder(self, rtItem):
        QDesktopServices.openUrl(QUrl('/'.join(rtItem.path)))

    def getLabel(self, templateNode, projNode):
        """ Either use the liral text inside <label> or look it
            up in the project node if there's a <label xpath="/x/path">
        """
        labelNode = templateNode.find("label")
        label = "TITLE_NOT_FOUND"
        if labelNode is not None:
            if "xpath" in labelNode.attrib:
                xpath = labelNode.attrib['xpath']
                label = projNode.find(xpath).text
            else:
                label = labelNode.text

        return label

    def openProject(self, rtItem):
        print rtItem.path
        # itemExt = path.splitext(rtItem.data()['filepath'])[1]
        # if itemExt == '.shp':
        #     AddVectorLayer(rtItem)
        # else:
        #     AddRasterLayer(rtItem)



class RepoTreeItem():
    LOADING = 'Loading...'
    program = None
    localdir = None

    def __init__(self, nItem, rtParent, path=[], loadlevels=1):

        self.qStdItem = QStandardItem(self.LOADING)

        # Set the data backwards so we can find this object later
        self.qStdItem.setData(self, Qt.UserRole)

        self.nItem = nItem
        self.type = nItem['node']['type']
        self.rtParent = rtParent
        self.depth = self._getDepth()
        self.path = path

        self.loaded = False

        # These are timestamps but they also serve as existence
        self.local = None
        self.remote = None
        self.queued = None

        # TODO: This is a hack for now but it gets us over the hump
        if len(self.path) == 0:
            self.path = ["CRB"]

        self.load(loadlevels)

    def reset(self):
        self.loaded = False

        self.loadtime = None

        self.local = False
        self.localDateTime = None
        self.remote = False
        self.queued = None
        self.qStdItem.setText(self.LOADING)

    def _getDepth(self):
        """
        Find the root parent and count the depth of this object
        :return:
        """
        depth = 1
        currParent = self.rtParent
        while type(currParent) == RepoTreeItem:
            depth +=1
            currParent = currParent.rtParent
        return depth

    def load(self, loadlevels):
        """
        Load a single item in the tree. This sets the name and color. Also gets the state of this item
        :param loadlevels:
        :return:
        """
        # For Groups
        if self.type == 'product':
            self.qStdItem.setText(self.nItem['node']['name'])
            self.qStdItem.setForeground(QBrush(QColor("#660000")))

        elif self.type == "group":
            self.qStdItem.setText(self.nItem['node']['folder'])
            self.qStdItem.setForeground(QBrush(QColor("#000066")))

        elif self.type == 'collection':
            try:
                # try and find a better name than just the folder name (not always possible)
                folderItem = next(
                    (d for d in self.nItem['node']['allows'] if d["folder"] == self.path[-1] and d['type'] == 'fixed'),
                    None)
                if folderItem is not None:
                    self.qStdItem.setText(folderItem['name'])
            except:
                pass

        self.recalcState()
        self.loadChildren((loadlevels - 1))

    def recalcState(self):
        """
        All important state function. This tells us a lot about what's new, what's old and what exists
        :return:
        """
        s3path = '/'.join(self.path)
        localpath = path.join(RepoTreeItem.localdir, path.sep.join(self.path))
        if self.type == "product":
            head = s3HeadData(RepoTreeItem.program.Bucket, s3path)
            self.local = path.isfile(localpath)
        elif self.type == 'group':
            self.remote = s3Exists(RepoTreeItem.program.Bucket, s3path)
            self.local = path.isdir(localpath)
        elif self.type == 'collection':
            # With collections we've already done our checking with a directory list
            # So we assume the remote
            self.remote = True
            self.local = path.isdir(localpath)

        self.loadtime = datetime.datetime.now()
        self.loaded = True


    def loadChildren(self, loadlevels):
        if loadlevels < 1 or self.type == 'product':
            return

        for child in self.nItem['children']:
            # Add the leaf to the tree
            pathstr = '/'.join(self.path) + '/' if len(self.path) > 0 else ""
            type = child['node']['type']

            if type == 'product':
                # End of the line
                newpath = self.path[:]
                newpath.append(child['node']['folder'])
                newpath.append(RepoTreeItem.program.ProjectFile)
                newTreeItem = RepoTreeItem(child, self, newpath, loadlevels=loadlevels)
                self.qStdItem.appendRow(newTreeItem.qStdItem)

            elif type == 'group':
                newpath = self.path[:]
                newpath.append(child['node']['folder'])
                newTreeItem = RepoTreeItem(child, self, newpath, loadlevels=loadlevels)
                self.qStdItem.appendRow(newTreeItem.qStdItem)

            elif type == 'collection':
                # Unfortunately the only way to list collections is to go get them physically.
                for levelname in s3GetFolderList(RepoTreeItem.program.Bucket, pathstr):
                    newpath = self.path[:]
                    newpath.append(levelname)
                    newTreeItem = RepoTreeItem(child, self, newpath, loadlevels=loadlevels)
                    self.qStdItem.appendRow(newTreeItem.qStdItem)
