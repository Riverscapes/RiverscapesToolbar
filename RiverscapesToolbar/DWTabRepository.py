from PyQt4.QtGui import QMenu, QDesktopServices
from PyQt4.QtCore import Qt, QUrl
from os import path
from DWTabProject import DockWidgetTabProject
from DWTabRepositoryItem import RepoTreeItem


class DockWidgetTabRepository():

    treectl = None
    START_LEVELS = 2

    def __init__(self, dockWidget):
        # used to be:
        # def __init__(self, xmlPath, treeControl, parent=None):
        # Connect up our buttons to functions
        self.dockwidget = dockWidget

        # Set as static so we can find it.
        DockWidgetTabRepository.treectl = dockWidget.treeRepository
        self.treectl.setAlternatingRowColors(True)
        self.treectl.setContextMenuPolicy(Qt.CustomContextMenu)

        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)

        self.treectl.customContextMenuRequested.connect(self.openMenu)
        self.treectl.doubleClicked.connect(self.treedoubleclick)
        self.treectl.itemExpanded.connect(self.expandItem)

        dockWidget.btnRefresh.clicked.connect(self.refreshRoot)
        self.refreshRoot()

    def expandItem(self, item):
        """
        Expand this item.
        :param item:
        :return:
        """
        item.data(0, Qt.UserRole).loadChildren()

    def refreshRoot(self):
        """
        Refresh the root of the main tree
        :return:
        """
        self.dockwidget.btnRefresh.setText("Loading...")
        self.dockwidget.btnRefresh.setEnabled(False)

        DockWidgetTabRepository.treectl.takeTopLevelItem(0)
        rootItem = RepoTreeItem(loadlevels = self.START_LEVELS, treectl=self.treectl)
        self.treectl.expandToDepth(self.START_LEVELS - 2)

        self.dockwidget.btnRefresh.setEnabled(True)
        self.dockwidget.btnRefresh.setText("Refresh")

    def treedoubleclick(self, index):
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        if theData.type=="product" and theData.local:
            self.openProject(theData)


    def openMenu(self, pt):
        """
        Handle the contextual menu when right-clicking items in the tree
        :param pt: 
        :return: 
        """
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        menu = QMenu()
        refreshReceiver = lambda item=theData: item.refreshAction()

        if (theData.type=="product"):
            openReceiver = lambda item=theData: self.openProject(item)
            downloadReceiver = lambda item=theData: self.addProjectToDownloadQueue(item)
            uploadReceiver = lambda item=theData: self.addProjectToUploadQueue(item)
            findFolderReceiver = lambda item=theData: self.findFolder(item)

            openAction = menu.addAction("Open Project", openReceiver)
            menu.addSeparator()
            downAction = menu.addAction("Download Project", downloadReceiver)
            uploAction = menu.addAction("Upload Project", uploadReceiver)
            menu.addSeparator()
            refreshAction = menu.addAction("Refresh", refreshReceiver)
            findAction = menu.addAction("Find Folder", findFolderReceiver)

            # The actions are available if the projects are available locally or otherwise
            openAction.setEnabled(theData.local)
            downAction.setEnabled(theData.remote)
            uploAction.setEnabled(theData.local)
            findAction.setEnabled(theData.local)

        else:
            dwnQueueReceiver = lambda item=theData: self.openProject(item)
            queueContainerAction = menu.addAction("Add projects to Download Queue", dwnQueueReceiver)
            refreshAction = menu.addAction("Refresh", refreshReceiver)

            queueContainerAction.setEnabled(True)

        menu.exec_(self.treectl.mapToGlobal(pt))

    def addProjectToDownloadQueue(self, rtItem):
        print "Adding to download Queue: " + '/'.join(rtItem.pathArr)

    def addProjectToUploadQueue(self, rtItem):
        print "Adding to Upload Queue: " + '/'.join(rtItem.pathArr)

    def findFolder(self, rtItem):
        qurl = QUrl.fromLocalFile(path.join(RepoTreeItem.localdir, path.sep.join(rtItem.pathArr[:-1])))
        QDesktopServices.openUrl(qurl)

    def openProject(self, rtItem):
        print "OPEN THE PROJECT"
        localpath = path.join(RepoTreeItem.localdir, path.sep.join(rtItem.pathArr))
        # Switch to the project tab
        self.dockwidget.tabWidget.setCurrentIndex(self.dockwidget.PROJECT_TAB)
        DockWidgetTabProject.projectLoad(localpath)



