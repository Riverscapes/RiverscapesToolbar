from PyQt4.QtGui import QMenu, QDesktopServices, QIcon
from PyQt4.QtCore import Qt, QUrl
from os import path, makedirs

from DWTabRepositoryItem import RepoTreeItem

from lib.s3.operations import S3Operation
from AddQueueDialog import AddQueueDialog
from resources import qTreeIconStates

class DockWidgetTabRepository():

    treectl = None
    START_LEVELS = 2
    dockwidget = None

    def __init__(self, dockWidget):

        # Connect up our buttons to functions
        DockWidgetTabRepository.dockwidget = dockWidget

        # Set as static so we can find it.
        DockWidgetTabRepository.treectl = dockWidget.treeRepository
        self.treectl.setAlternatingRowColors(True)
        self.treectl.setContextMenuPolicy(Qt.CustomContextMenu)

        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)

        RepoTreeItem.showNon = dockWidget.btnShowNon.isChecked()

        self.treectl.customContextMenuRequested.connect(self.openMenu)
        self.treectl.doubleClicked.connect(self.treedoubleclick)
        self.treectl.itemExpanded.connect(self.expandItem)

        dockWidget.btnShowNon.clicked.connect(self.showNonexistent)
        dockWidget.btnShowNon.setIcon(QIcon(qTreeIconStates.HIDDEN))

        dockWidget.btnReload.clicked.connect(self.reloadRoot)
        dockWidget.btnReload.setIcon(QIcon(qTreeIconStates.RELOAD))

        dockWidget.btnLocalOnly.clicked.connect(self.localOnly)
        dockWidget.btnLocalOnly.setIcon(QIcon(qTreeIconStates.UNPLUG))

        self.reloadRoot()

    def localOnly(self, value):
        # If we're turning this on we can refresh but if we're turning it off we have to reload
        RepoTreeItem.localOnly = value
        if value:
            self.refreshRoot()
        else:
            self.reloadRoot()


    def expandItem(self, item):
        """
        Expand this item.
        :param item:
        :return:
        """
        item.data(0, Qt.UserRole).load()

    def showNonexistent(self, value):
        RepoTreeItem.showNon = value
        self.refreshRoot()

    def reloadRoot(self):
        """
        Reloads the root of the main tree
        This will cause all the network lookups to happen again
        :return:
        """
        self.dockwidget.btnReload.setText("Loading...")
        self.dockwidget.btnReload.setEnabled(False)

        DockWidgetTabRepository.treectl.takeTopLevelItem(0)
        rootItem = RepoTreeItem(treectl=self.treectl)
        rootItem.load(self.START_LEVELS)
        self.treectl.expandToDepth(self.START_LEVELS - 2)

        self.dockwidget.btnReload.setEnabled(True)
        self.dockwidget.btnReload.setText("Reload")

    def refreshRoot(self):
        """
        Refresh the root of the main tree
        :return:
        """
        rootItem = DockWidgetTabRepository.treectl.topLevelItem(0)
        rootItemData = rootItem.data(0, Qt.UserRole)
        rootItemData.forwardRefresh()


    def treedoubleclick(self, index):
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        if theData.type=="product" and theData.local:
            self.dockwidget.TabProject.openProject(theData)


    def createFolder(self, rtItem):
        print "createfolder"
        if rtItem.type == "product":
            localpath = path.join(RepoTreeItem.localrootdir, path.sep.join(rtItem.pathArr[:-1]))
        else:
            localpath = path.join(RepoTreeItem.localrootdir, path.sep.join(rtItem.pathArr))

        if not path.isdir(localpath):
            try:
                makedirs(localpath)
            except Exception, e:
                pass

        qurl = QUrl.fromLocalFile(localpath)
        QDesktopServices.openUrl(qurl)
        self.refreshRoot()

    def openMenu(self, pt):
        """
        Handle the contextual menu when right-clicking items in the tree
        :param pt: 
        :return: 
        """
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        menu = QMenu()
        refreshReceiver = theData.refreshAction
        findFolderReceiver = lambda data=theData: self.findFolder(data)
        createFolderReceiver = lambda data=theData: self.createFolder(data)

        if (theData.type=="product"):

            openReceiver = lambda data=theData: self.dockwidget.TabProject.openProject(data)
            downloadReceiver = lambda data=theData: self.addProjectToDownloadQueue(data)
            uploadReceiver = lambda data=theData: self.addProjectToUploadQueue(data)

            openAction = menu.addAction("Open Project", openReceiver)

            # If we're restricting things to local only there's no need for uploading or downloading
            menu.addSeparator()
            downAction = menu.addAction("Download Project", downloadReceiver)
            uploAction = menu.addAction("Upload Project", uploadReceiver)
            downAction.setEnabled(theData.remote and not RepoTreeItem.localOnly)
            uploAction.setEnabled(theData.local and not RepoTreeItem.localOnly)

            if theData.remote or theData.local:
                menu.addSeparator()

                refreshAction = menu.addAction("Reload", refreshReceiver)
                refreshAction.setEnabled(True)
                findAction = menu.addAction("Find Folder", findFolderReceiver)
                findAction.setEnabled(theData.local)

            if (not theData.local):
                createFolderAction = menu.addAction("Create Folder", createFolderReceiver)

            # The actions are available if the projects are available locally or otherwise
            openAction.setEnabled(theData.local)

        # Groups and containers
        else:
            dwnQueueReceiver = lambda data=theData: self.dockwidget.TabProject.openProject(data)
            refreshAction = menu.addAction("Reload", refreshReceiver)
            refreshAction.setEnabled(True)
            menu.addSeparator()
            # queueContainerAction = menu.addAction("Add projects to Download Queue", dwnQueueReceiver)
            # queueContainerAction.setEnabled(True)
            findAction = menu.addAction("Find Folder", findFolderReceiver)
            findAction.setEnabled(theData.local)

            if (not theData.local):
                createFolderAction = menu.addAction("Create Folder", createFolderReceiver)

        menu.exec_(self.treectl.mapToGlobal(pt))

    def addProjectToDownloadQueue(self, rtItem):
        print "Adding to download Queue: " + '/'.join(  rtItem.pathArr)
        dialog = AddQueueDialog(S3Operation.Direction.DOWN, rtItem)
        if dialog.exec_():
            self.dockwidget.TabDownload.addToQueue(dialog.qItem)

    def addProjectToUploadQueue(self, rtItem):
        print "Adding to Upload Queue: " + '/'.join(rtItem.pathArr)
        dialog = AddQueueDialog(S3Operation.Direction.UP, rtItem)
        if dialog.exec_():
            self.dockwidget.TabDownload.addToQueue(dialog.qItem)

    def findFolder(self, rtItem):
        if rtItem.type == "product":
            localpath = path.join(RepoTreeItem.localrootdir, path.sep.join(rtItem.pathArr[:-1]))
        else:
            localpath = path.join(RepoTreeItem.localrootdir, path.sep.join(rtItem.pathArr))
        qurl = QUrl.fromLocalFile(localpath)
        QDesktopServices.openUrl(qurl)

    @staticmethod
    def expandToProject(rtItem):
        DockWidgetTabRepository.treectl.setCurrentItem(rtItem.qTreeWItem)


