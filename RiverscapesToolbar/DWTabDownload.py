from os import path
from lib.s3.walkers import s3BuildOps
from lib.async import ToolbarQueues
from PyQt4.QtGui import QMenu, QDesktopServices, QListWidgetItem
from PyQt4.QtCore import Qt, QUrl, QObject, SIGNAL, SLOT
from settings import Settings
from program import Program
from lib.async import TreeLoadQueues

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

        # Columns: Projects:   Name, Progress  (--, 54%, DONE)

        # files: Op, localpath, size, progress (--, 54%, DONE)    

UI:
    - lstFiles rebuild on Project Change

"""

class DockWidgetTabDownload():
    treectl = None

    def __init__(self, dockWidget):
        print "init DockWidgetTabDownload"
        self.Qs = ToolbarQueues()
        self.settings = Settings()
        self.program = Program()

        self.dw = dockWidget
        self.Q = TreeLoadQueues()
        DockWidgetTabDownload.treectl = self.dw.treeProjQueue

        self.dw.btnDownloadStart.clicked.connect(self.startWorker)
        self.dw.btnDownloadPause.clicked.connect(self.stopWorker)

        self.dw.btnDownloadEmpty.clicked.connect(self.emptyQueue)
        self.dw.btnDownloadClearCompleted.clicked.connect(self.clearCompleted)

        self.dw.btnProjectRemove.clicked.connect(self.removeItemFromQueue)

        self.dw.treeProjQueue.setColumnCount(3)
        self.dw.treeProjQueue.setHeaderHidden(False)

        self.dw.treeProjQueue.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dw.treeProjQueue.customContextMenuRequested.connect(self.openMenu)

        # Hookup slots to our signals
        # self.Qs.Qstatus.connect(self.updateProgress)


    def updateProgBars(self, updateObj):
        self.dw.progProject = 3
        self.dw.progFile = 3
        self.dw.progOverall = 3
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


    def addItemToQueue(self, QueueItem):
        """
        :return: 
        """
        print "Now What?!?"
        # self.qTreeWItem = QListWidgetItem(DockWidgetTabDownload.treectl)
        #
        # # Set the data backwards so we can find this object later
        # self.qTreeWItem.setData(0, Qt.UserRole, self)
        # self.qTreeWItem.setText(0, "NAME")
        #
        # # Add yourself to the queue please
        # ToolbarQueues.project_q.put(self)

        # disconnect everything connected to myReadTimer's timeout
        # QObject.disconnect(myReadTimer, SIGNAL("setValue(int)"), 0, 0);

        # for key in self.opstore:
        #     self.opstore[key].execute()


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