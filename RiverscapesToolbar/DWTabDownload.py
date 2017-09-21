from os import path

from PyQt4.QtGui import QMenu, QIcon, QDesktopServices
from PyQt4.QtCore import Qt, QUrl
from settings import Settings
from lib.s3.operations import S3Operation
from resources import qTreeIconStates
from lib.async import ToolbarQueues

# Initialize our borg
Qs = ToolbarQueues()
settings = Settings()


class DockWidgetTabDownload():
    treectl = None
    dockwidget = None

    def __init__(self, dockWidget):
        print "init DockWidgetTabDownload"
        self.settings = Settings()

        # We reset this setting so you only ever get the Access denied error once
        settings.saveSetting("accessError", False)

        DockWidgetTabDownload.dockwidget = dockWidget
        DockWidgetTabDownload.treectl = self.dockwidget.treeProjQueue

        self.dockwidget.btnDownloadStart.clicked.connect(Qs.startWorker)
        self.dockwidget.btnDownloadStart.setIcon(QIcon(qTreeIconStates.PLAY))
        self.dockwidget.btnDownloadPause.clicked.connect(Qs.stopWorker)
        self.dockwidget.btnDownloadPause.setIcon(QIcon(qTreeIconStates.PAUSE))

        self.dockwidget.btnDownloadEmpty.clicked.connect(self.emptyQueueRequest)
        self.dockwidget.btnDownloadClearCompleted.clicked.connect(self.clearCompleted)

        self.dockwidget.btnProjectRemove.clicked.connect(self.removeItemFromQueue)

        self.dockwidget.treeProjQueue.setColumnCount(2)
        self.dockwidget.treeProjQueue.setHeaderHidden(False)

        # Override the resize event
        self.treectl.resizeEvent = self.resizeEvent

        self.dockwidget.treeProjQueue.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dockwidget.treeProjQueue.customContextMenuRequested.connect(self.openMenu)

    def resizeEvent(self, event):
        width = self.dockwidget.treeProjQueue.width()
        self.dockwidget.treeProjQueue.setColumnWidth(1, width * 0.1999)
        self.dockwidget.treeProjQueue.setColumnWidth(0, width * 0.8)

    @staticmethod
    def addToQueue(QueueItem):
        settings.saveSetting("accessError", False)
        DockWidgetTabDownload.dockwidget.tabWidget.setCurrentIndex(DockWidgetTabDownload.dockwidget.DOWNLOAD_TAB)
        QueueItem.addItemToQueue()

    def openMenu(self, pt):
        """
        Handle the contextual menu when right-clicking items in the tree
        :param pt: 
        :return: 
        """
        item = self.treectl.selectedIndexes()[0]

        theProject = item.data(Qt.UserRole)[0]
        theOp =  item.data(Qt.UserRole)[1]
        menu = QMenu()

        # Remove/Clear completed
        # Is this a root node or a child
        if isinstance(theOp, S3Operation):
            # Child ==> Op ==> Individual file options
            findReceiver = lambda: self.findFolder(theOp.abspath)
            findReceiverAction = menu.addAction("Find file", findReceiver)
            findReceiverAction.setEnabled(path.isfile(theOp.abspath))
        else:
            # root node ==> Project
            rootDir = theProject.getAbsProjRoot()
            projFile = theProject.getAbsProjFile()
            findReceiver = lambda: self.findFolder(rootDir)

            findinrepoReceiver = lambda: self.findInRepo(theProject)
            openProjectReceiver = lambda: self.dockwidget.TabProject.openProject(theProject)

            findinrepoReceiverAction = menu.addAction("Find project folder", findReceiver)
            locateReceiverAction = menu.addAction("Locate in Repository", findinrepoReceiver)
            openProjectReceiverAction = menu.addAction("Open Project", openProjectReceiver)
            progress = 100
            done = progress == 100

            findinrepoReceiverAction.setEnabled(path.isdir(rootDir))
            locateReceiverAction.setEnabled(True)
            openProjectReceiverAction.setEnabled(path.isfile(projFile))


        menu.exec_(self.treectl.mapToGlobal(pt))

    def findFolder(self, filepath):
        if path.isfile(filepath):
            qurl = QUrl.fromLocalFile(path.dirname(filepath))
        else:
            qurl = QUrl.fromLocalFile(filepath)
        QDesktopServices.openUrl(qurl)

    def findInRepo(self, project):
        self.dockwidget.TabRepo.expandToProject(project)
        self.dockwidget.tabWidget.setCurrentIndex(self.dockwidget.REPO_TAB)


    def emptyQueueRequest(self):
        print "empty queue"
        Qs.stopWorker()
        Qs.resetQueue()

        for idx in range(self.treectl.topLevelItemCount()):
            self.treectl.takeTopLevelItem(idx)

    def clearCompleted(self):
        print "clear completed"
        for idx in range(0, self.treectl.topLevelItemCount()):
            child = self.treectl.topLevelItem(idx)
            theData = child.data(0, Qt.UserRole)[0]
            if theData.qItem.progress == 100:
                taken = self.treectl.takeTopLevelItem(idx)

    def removeItemFromQueue(self):
        """
        :return: 
        """
        for item in self.treectl.selectedItems():
            idx = self.treectl.indexOfTopLevelItem(item)
            taken = self.treectl.takeTopLevelItem(idx)


    def recalcState(self):
        print "do it"


