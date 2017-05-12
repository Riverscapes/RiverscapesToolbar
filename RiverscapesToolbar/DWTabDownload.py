from os import path
from lib.s3.walkers import s3BuildOps
from PyQt4.QtGui import QMenu, QTreeWidgetItem, QIcon
from PyQt4.QtCore import Qt, QObject, pyqtSlot
from settings import Settings
from program import Program
from lib.async import ToolbarQueues
from lib.treeitem import *
from lib.s3.operations import S3Operation


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
        self.dockwidget.btnDownloadPause.clicked.connect(Qs.stopWorker)

        self.dockwidget.btnDownloadEmpty.clicked.connect(self.emptyQueue)
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
        theData = item.data(Qt.UserRole)

        menu = QMenu()

        # Remove/Clear completed
        # goto Folder
        if (theData.type=="product"):
            openReceiver = lambda item=theData: self.openProject(item)
            openReceiverAction = menu.addAction("Add projects to Download Queue", openReceiver)
            openReceiverAction.setEnabled(theData.local)
            openReceiverAction.setEnabled(True)

        menu.exec_(self.treectl.mapToGlobal(pt))

    def loadProject(dlg):
        print "Download loaded"

    def clearQueue(self):
        print "empty queue"

    def emptyQueue(self):
        print "empty queue"

    def clearCompleted(self):
        print "clear completed"


    def removeItemFromQueue(self, item):
        """
        :return: 
        """
        print "hello"

    def recalcState(self):
        """
        Here's where we update all the progress bars and the title card
        with "Queue (15%)"
        :return:
        """

        # lbl_QueueStatus
        # lbl_ProjectStatus
        # lbl_FileStatus


        # if project selected then removebtn enabled
        print "here"


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

    def __init__(self, rtItem, conf):
        # This object gets passed around a lot so we package it up
        self.name = rtItem.name
        self.rtItem = rtItem
        self.conf = conf
        self.qTreeWItem = None
        self.opstore = s3BuildOps(self.conf)

        # for key,op in self.opstore.iteritems():
        #     op.s3.progsignal.connect(self.updateTransferProgress)

    def updateProjectStatus(self, statusInt = None):
        if statusInt is not None:
            self.qTreeWItem.setText(1, "{}%".format(statusInt))
        else:
            totalprog = 0
            counter = 0
            for key, op in self.opstore.iteritems():
                totalprog += op.progress
                counter += 1
            self.qTreeWItem.setText(1, "{}%".format(totalprog / (counter * 100)))

    @pyqtSlot()
    def updateTransferProgress(self, progtuple):
        print "DWTabDownload: {} -- {}".format(progtuple[0], progtuple[1])
        for idx in range(self.qTreeWItem.childCount()):
            child = self.qTreeWItem.child(idx)
            if child.data(0, Qt.UserRole) == progtuple[0]:
                child.setText(1, "{}%".format(progtuple[1]))
        self.updateProjectStatus()

    def addItemToQueue(self):

        # Create a tree Item for this and then push it onto the Queue
        self.qTreeWItem = QTreeWidgetItem(DockWidgetTabDownload.treectl)

        if self.conf.direction == S3Operation.Direction.DOWN:
            icon = QIcon(qTreeIconStates.DOWNLOAD)
        else:
            icon = QIcon(qTreeIconStates.UPLOAD)

        self.qTreeWItem.setText(0, self.rtItem.getRemoteS3Prefix())
        self.qTreeWItem.setText(1, "Queued")
        self.qTreeWItem.setIcon(1, icon)

        # Set the data backwards so we can find this object later
        self.qTreeWItem.setData(0, Qt.UserRole, self.rtItem)
        setFontBold(self.qTreeWItem, 0)
        for key, op in self.opstore.iteritems():
            newTransferItem = QTreeWidgetItem(self.qTreeWItem)
            newTransferItem.setText(0, op.key)
            newTransferItem.setText(1, "Queued")
            newTransferItem.setIcon(1, icon)
            setFontColor(newTransferItem, "#666666", 0)
            newTransferItem.setData(0, Qt.UserRole, op)

        Qs.queuePush(self)

        DockWidgetTabDownload.treectl.sortItems(0, Qt.AscendingOrder)


class qTreeIconStates:
    """
    Think of this like an enumeration for icons
    """
    """
            <file alias="caret_down_green.png">images/icons/font-awesome_4-7-0_caret-down_12_0_27ae60_none.png</file>
            <file alias="caret_up_blue.png">images/icons/font-awesome_4-7-0_caret-up_12_0_2980b9_none.png</file>
    
    """
    DOWNLOAD = ":/plugins/RiverscapesToolbar/caret_down_green.png"
    UPLOAD = ":/plugins/RiverscapesToolbar/caret_up_blue.png"

