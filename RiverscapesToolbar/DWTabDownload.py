from os import path
from lib.s3.walkers import s3BuildOps
from lib.async import ToolbarQueues
from PyQt4.QtGui import QMenu, QTreeWidgetItem, QIcon
from PyQt4.QtCore import Qt, SIGNAL, SLOT
from settings import Settings
from program import Program
from lib.async import TreeLoadQueues
from lib.treeitem import *
from lib.s3.operations import S3Operation


"""
Ok, so here's the hierarchy

DockWidgetTabDownload
    lstProjs
        Rows
            data ==> ProjectTransfer()
                opstore = {filepath: S3Operation}
                    self.s3 = FileTransfer(conf.bucket)
                        Progress                        
                    self.key = key            
                    self.filestate = LOCALONLY,REMOTEONLY,UPDATENEEDED,SAME                      
                    self.op = DELETE_REMOTE, DELETE_LOCAL, UPLOAD, DOWNLOAD, IGNORE
                    self.s3size = 0                    

        # Columns: Projects:   Direction, Name, Progress  (--, 54%, DONE)

        # files: Op, localpath, size, progress (--, 54%, DONE)    

UI:
    - lstFiles rebuild on Project Change

"""

Qs = ToolbarQueues()
settings = Settings()


class DockWidgetTabDownload():
    treectl = None
    dockwidget = None

    def __init__(self, dockWidget):
        print "init DockWidgetTabDownload"
        self.Qs = ToolbarQueues()
        self.settings = Settings()
        self.program = Program()

        DockWidgetTabDownload.dockwidget = dockWidget
        self.Q = TreeLoadQueues()
        DockWidgetTabDownload.treectl = self.dockwidget.treeProjQueue

        self.dockwidget.btnDownloadStart.clicked.connect(self.startWorker)
        self.dockwidget.btnDownloadPause.clicked.connect(self.stopWorker)

        self.dockwidget.btnDownloadEmpty.clicked.connect(self.emptyQueue)
        self.dockwidget.btnDownloadClearCompleted.clicked.connect(self.clearCompleted)

        self.dockwidget.btnProjectRemove.clicked.connect(self.removeItemFromQueue)

        self.dockwidget.treeProjQueue.setColumnCount(2)
        self.dockwidget.treeProjQueue.setHeaderHidden(False)

        self.dockwidget.treeProjQueue.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dockwidget.treeProjQueue.customContextMenuRequested.connect(self.openMenu)

        # Hookup slots to our signals
        # self.Qs.Qstatus.connect(self.updateProgress)


    def updateProgBars(self, updateObj):

        print "whoa"


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

    def startWorker(self):
        self.Qs.startWorker()

    def stopWorker(self):
        self.Qs.stopWorker()

    def emptyQueue(self):
        print "empty queue"

    def clearCompleted(self):
        print "clear completed"

    @staticmethod
    def addItemToQueue(QueueItem):
        """
        
        :param QueueItem: 
        :return: 
        """

        # Create a tree Item for this and then push it onto the Queue
        newProjItem = QTreeWidgetItem(DockWidgetTabDownload.treectl)

        if QueueItem.conf.direction == S3Operation.Direction.DOWN:
            icon = QIcon(qTreeIconStates.DOWNLOAD)
        else:
            icon = QIcon(qTreeIconStates.UPLOAD)

        newProjItem.setText(0, QueueItem.rtItem.getRemoteS3Prefix())
        newProjItem.setText(1, "Queued")
        newProjItem.setIcon(1, icon)

        # Set the data backwards so we can find this object later
        newProjItem.setData(0, Qt.UserRole, QueueItem.rtItem)
        setFontBold(newProjItem,0)
        for key, op in QueueItem.opstore.iteritems():
            newTransferItem = QTreeWidgetItem(newProjItem)
            newTransferItem.setText(0, op.key)
            newTransferItem.setText(1, "Queued")
            newTransferItem.setIcon(1, icon)
            setFontColor(newTransferItem, "#666666", 0)
        Qs.queuePush(QueueItem)

        DockWidgetTabDownload.treectl.sortItems(0, Qt.AscendingOrder)


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


class QueueItem():

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
        self.opstore = s3BuildOps(self.conf)

    def progress(self):
        self.progress = 100


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

