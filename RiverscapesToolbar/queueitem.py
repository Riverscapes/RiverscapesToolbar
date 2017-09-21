from lib.treeitem import *
from lib.s3.walkers import s3BuildOps
from lib.s3.operations import S3Operation
from PyQt4.QtCore import Qt, QObject, pyqtSignal
from PyQt4.QtGui import QTreeWidgetItem, QIcon, QMessageBox
from settings import Settings
from resources import qTreeIconStates
from lib.async import ToolbarQueues
from DWTabDownload import DockWidgetTabDownload

Qs = ToolbarQueues()

class QueueItem(QObject):

    progsignal = pyqtSignal(object)

    class States:

        WAITING = {
            "color": "#666666",
            "styler": setFontRegular,
        }
        IGNORED = {
            "color": "#666666",
            "styler": setFontItalic,
        }
        COMPLETE = {
            "color": "#000000",
            "styler": setFontBold,
        }
        INPROGRESS = {
            "color": "#000000",
            "styler": setFontRegular,
        }
        FAILED = {
            "color": "#FF0000",
            "styler": setFontRegular,
        }


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
        self.status = QueueItem.States.WAITING
        self.qTreeWItem = None
        self.opstore = s3BuildOps(self.conf, self.updateTransferProgress)

    def updateProjectStatus(self):
        """
        Update the status of the top-level tree items in the download queue
        :return:
        """
        if self.status == QueueItem.States.COMPLETE:
            return

        anyInProgress = any(op.runState == S3Operation.RunStates.INPROGRESS for op in self.opstore.itervalues())
        anyErrors = any(op.runState == S3Operation.RunStates.ERROR for op in self.opstore.itervalues())
        allComplete = all(op.runState == S3Operation.RunStates.COMPLETE for op in self.opstore.itervalues())
        allIgnored = all(op.op == S3Operation.FileOps.IGNORE for op in self.opstore.itervalues())

        totalprogpercent = 0
        progstr = ""

        if allComplete:
            self.status = QueueItem.States.COMPLETE
            totalprogpercent = 100
            progstr = "Done"
        elif allIgnored:
            self.status = QueueItem.States.IGNORED
            progstr = "Ignored"
        else:
            if anyErrors:
                self.status = QueueItem.States.FAILED
                settings = Settings()
                if settings.getSetting("accessError") == False:
                    settings.saveSetting("accessError", True)
                    DockWidgetTabDownload.dockwidget.showMessageBox.emit("Access Denied", "Some/all of your queued transactions failed due to access denied errors. If your uploads are failing then you may need a new set of AWS keys. Please contact the program administrators to get this fixed.", "", QMessageBox.Critical)
                    # okDlg("Access Denied", infoText="Some/all of your queued transactions failed due to access denied errors. If your uploads are failing then you may need a new set of AWS keys. Please contact the program administrators to get this fixed.", icon=QMessageBox.Critical)
            if anyInProgress:
                self.status = QueueItem.States.INPROGRESS

            totalprog = 0
            totaljobs = self.qTreeWItem.childCount()
            totaldone = totaljobs - len(self.opstore)
            for key, op in self.opstore.iteritems():
                totalprog += float(op.progress) / 100

            totalprogpercent = 100 * (totalprog + totaldone) / totaljobs
            progstr = "{:.2f}%".format(totalprogpercent)

        self.progress = totalprogpercent
        self.qTreeWItem.setText(1, progstr)

        setFontColor(self.qTreeWItem, self.status["color"], 1)
        setFontColor(self.qTreeWItem, self.status["color"], 0)
        self.status["styler"](self.qTreeWItem, 1)
        self.status["styler"](self.qTreeWItem, 0)

        settings = Settings()


    def updateTransferProgress(self, op):
        """
        Update the sub-items (individual files) in the transfer queue
        :param op: Op is the S3Operations object
        :return:
        """
        for idx in range(self.qTreeWItem.childCount()):
            child = self.qTreeWItem.child(idx)
            if child.data(0, Qt.UserRole)[1].abspath == op.abspath:
                status = QueueItem.States.WAITING
                progstr = "--"
                child.setToolTip(0, "File is waiting in queue.")

                if op.runState == S3Operation.RunStates.COMPLETE:
                    progstr = "Done"
                    status = QueueItem.States.COMPLETE
                    child.setToolTip(0, "Done. File has been downloaded")

                elif op.op == S3Operation.FileOps.IGNORE:
                    progstr = "Ignored"
                    status = QueueItem.States.IGNORED
                    child.setToolTip(0, "File ignored.")

                elif op.runState == S3Operation.RunStates.ERROR:
                    progstr = "Error"
                    status = QueueItem.States.FAILED
                    child.setToolTip(0, op.error)
                    child.setToolTip(1, op.error)
                    icon = QIcon(qTreeIconStates.ERROR)
                    child.setIcon(1, icon)

                elif op.runState == S3Operation.RunStates.INPROGRESS:
                    status = QueueItem.States.INPROGRESS
                    progstr = "{}%".format(op.status)
                    child.setToolTip(0, "Downloading in progress.")

                child.setText(1, progstr)

                setFontColor(child, status["color"], 1)
                setFontColor(child, status["color"], 0)
                status["styler"](child, 1)
                status["styler"](child, 0)

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
            newTransferItem.setIcon(1, icon)
            newTransferItem.setData(0, Qt.UserRole, [self.project, op])
            self.updateTransferProgress(op)

        allIgnored = all(op.op == S3Operation.FileOps.IGNORE for op in self.opstore.itervalues())

        if not allIgnored:
            # Now push the item onto the Download Queue Borg
            Qs.queuePush(self)

        # Now sort all the items
        DockWidgetTabDownload.treectl.sortItems(0, Qt.AscendingOrder)
        self.updateProjectStatus()