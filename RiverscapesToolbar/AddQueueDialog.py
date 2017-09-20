from os import path
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal, QTemporaryFile
import PyQt4.uic as uic
from settings import Settings
from program import Program
from lib.treeitem import *
from lib.s3.operations import S3Operation
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtCore import Qt
from project import Project
from DWTabDownload import QueueItem

FORM_CLASS, _ = uic.loadUiType(path.join(path.dirname(__file__), 'AddQueueDialog.ui'))

settings = Settings()
# Do we have the program XML yet? If not, go get it.
program = Program()


class AddQueueDialog(QtGui.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, direction, project):
        """Constructor."""
        super(AddQueueDialog, self).__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.loading = True
        self.direction = direction
        self.project = project

        # Keep things on top
        self.setWindowTitle("Riverscapes Add to Down/Upload Queue")
        self.lblState.setText("")
        # Map settings keys to their respective text boxes
        self.lblState.setStyleSheet('QLabel { color: red }')

        # Map functions to click events
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.close)

        isRemote = self.direction == S3Operation.Direction.DOWN
        self.project.load(remote=isRemote)

        # TODO: Delete and force should probably come from the dialog, not settings.
        if program.valid:
            conf = QueueItem.TransferConf(program.Bucket, self.project.localprojroot, self.project.remotePrefix, self.direction,
                                          settings.getSetting("force"),
                                          settings.getSetting("delete"))

            self.qItem = QueueItem(self.project, conf)
            self.setMetaData()
            self.populateList()

    def setMetaData(self):
        """
        We display metadata before operations
        :return:
        """
        rows = [
            {"name": "Project Name", "value": self.project.projname },
            {"name": "Project Type", "value": self.project.projtype },
            {"name": "Remote Path", "value": self.project.remotePrefix },
            {"name": "Local Path", "value": self.project.absProjectFile},
        ]

        for row in self.project.meta:
            newItem = QTreeWidgetItem(self.treeMeta)
            setFontBold(newItem, column=0)
            newItem.setText(0, row['name'])
            newItem.setText(1, row['value'])

    def populateList(self):
        # If this is an upload then cram some
        for key,op in self.qItem.opstore.iteritems():
            newItem = QTreeWidgetItem(self.treeFiles)
            newItem.setText(0, op.op)

            if op.direction == S3Operation.Direction.DOWN:
                destpath = op.abspath
            else:
                # Uploads need a special path
                destpath = '/'.join(['s3://', op.bucket, op.fullkey])

            newItem.setText(1, destpath)

        if (len(self.treeFiles.children()) == 0):
            self.lblState.setText("No file operations queued. Nothing to do")
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        self.treeFiles.sortItems(1, Qt.AscendingOrder)