from os import path
from lib.s3.walkers import s3BuildOps
from PyQt4.QtGui import QMenu, QTreeWidgetItem, QIcon, QDesktopServices
from PyQt4.QtCore import Qt, QObject, pyqtSlot, QUrl
from settings import Settings
from program import Program
from project import Project
from lib.async import ToolbarQueues, QueueStatus
from lib.treeitem import *
from lib.s3.operations import S3Operation
from resources import qTreeIconStates

Qs = ToolbarQueues()
settings = Settings()


class DockWidgetTabDownload():
    treectl = None
    dockwidget = None

    def __init__(self, dockWidget):
        print "init DockWidgetTabDownload"
        self.settings = Settings()
        self.program = Program()

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

        self.dockwidget.treeProjQueue.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dockwidget.treeProjQueue.customContextMenuRequested.connect(self.openMenu)


    @staticmethod
    def addToQueue(QueueItem):
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


class QueueItem(QObject):

    class TransferConf():
        # This object gets passed around a lot so we package it up
        def __init__(self, bucket, localroot, keyprefix, direction, force=False, delete=False):
            self.delete = delete
            self.force = force
            self.direction = direction
            self.localroot = localroot
            self.keyprefix = keyprefix
            self.bucket = bucket

    def __init__(self, project, conf):
        # This object gets passed around a lot so we package it up
        self.name = project.projname
        self.project = project
        self.conf = conf
        self.progress = 0
        self.qTreeWItem = None
        self.opstore = s3BuildOps(self.conf, self.updateTransferProgress)

    def updateProjectStatus(self, statusInt = None):
        if statusInt is not None:
            self.progress = statusInt
            self.qTreeWItem.setText(1, "{}%".format(statusInt))
        else:
            totalprog = 0
            totaljobs = self.qTreeWItem.childCount()
            totaldone = totaljobs - len(self.opstore)
            for key, op in self.opstore.iteritems():
                totalprog += float(op.progress) / 100

            totalprogpercent = 100 * (totalprog + totaldone) / totaljobs
            if totalprogpercent < 100:
                progstr = "{:.2f}%".format(totalprogpercent)
            else:
                progstr = "Done"
            self.progress = totalprogpercent
            self.qTreeWItem.setText(1, progstr)

    def updateTransferProgress(self, progtuple):
        # print "DWTabDownload: {} -- {} -- {} -- {}".format(*progtuple)
        for idx in range(self.qTreeWItem.childCount()):
            child = self.qTreeWItem.child(idx)
            if child.data(0, Qt.UserRole)[1].abspath == progtuple[0]:
                if progtuple[1] < 100:
                    progstr = "{}%".format(progtuple[1])
                else:
                    progstr = "Done"
                child.setText(1, progstr)
        self.updateProjectStatus()

    def addItemToQueue(self):

        # Create a tree Item for this and then push it onto the Queue
        self.qTreeWItem = QTreeWidgetItem(DockWidgetTabDownload.treectl)

        if self.conf.direction == S3Operation.Direction.DOWN:
            icon = QIcon(qTreeIconStates.DOWNLOAD)
        else:
            icon = QIcon(qTreeIconStates.UPLOAD)

        self.qTreeWItem.setText(0, self.project.getRemoteS3Prefix())
        self.qTreeWItem.setText(1, "Queued")
        self.qTreeWItem.setIcon(1, icon)

        # Set the data backwards so we can find this object later
        self.project.qItem = self
        self.qTreeWItem.setData(0, Qt.UserRole, [self.project, None])
        setFontBold(self.qTreeWItem, 0)
        for key, op in self.opstore.iteritems():
            newTransferItem = QTreeWidgetItem(self.qTreeWItem)
            newTransferItem.setText(0, op.key)
            newTransferItem.setText(1, "--")
            newTransferItem.setIcon(1, icon)
            setFontColor(newTransferItem, "#666666", 0)
            newTransferItem.setData(0, Qt.UserRole, [self.project, op])

        Qs.queuePush(self)

        DockWidgetTabDownload.treectl.sortItems(0, Qt.AscendingOrder)
