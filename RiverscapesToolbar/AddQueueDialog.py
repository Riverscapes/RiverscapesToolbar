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

from DWTabDownload import QueueItem

FORM_CLASS, _ = uic.loadUiType(path.join(
    path.dirname(__file__), 'AddQueueDialog.ui'))

settings = Settings()
# Do we have the program XML yet? If not, go get it.
program = Program()


class AddQueueDialog(QtGui.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, direction, rtItem):
        """Constructor."""
        super(AddQueueDialog, self).__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.loading = True
        self.direction = direction
        self.rtItem = rtItem

        # Keep things on top
        self.setWindowTitle("Riverscapes Add to Down/Upload Queue")
        self.lblState.setText("")
        # Map settings keys to their respective text boxes
        self.lblState.setStyleSheet('QLabel { color: red }')

        # Map functions to click events
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.close)

        self.localprojroot = self.rtItem.getAbsProjRoot()
        self.keyprefix = self.rtItem.getRemoteS3Prefix()

        # TODO: Delete and force should probably come from the dialog, not settings.
        conf = QueueItem.TransferConf(program.Bucket, self.localprojroot, self.keyprefix, self.direction,
                                      settings.getSetting("force"),
                                      settings.getSetting("delete"))
        self.qItem = QueueItem(self.rtItem, conf)
        self.setMetaData()
        self.populateList()

    def setMetaData(self):
        # Downloads Don't get metadata because we don't have
        from lib.s3.comparison import getS3getFileContents
        import xml.etree.ElementTree as ET
        from StringIO import StringIO

        if self.direction == S3Operation.Direction.DOWN:
            projkey = path.join(self.rtItem.getRemoteS3Prefix(), program.ProjectFile)
            xmlstr = getS3getFileContents(program.Bucket, projkey)
            self.DOM = ET.fromstring(xmlstr)
        else:
            projfile = path.join(self.rtItem.getAbsProjFile())
            self.DOM = ET.parse(projfile)

        # Set up name and type
        rows = [
            {"name": "Project Name", "value": self.DOM.find('Name').text.strip()},
            {"name": "Project Type", "value": self.DOM.find('ProjectType').text.strip()},
            {"name": "Remote Path", "value": self.rtItem.getRemoteS3Prefix()},
            {"name": "Local Path", "value": self.rtItem.getAbsProjFile()},
        ]

        # Now print all the metadata values for reference
        metaNodes = self.DOM.findall('MetaData/Meta')
        for node in metaNodes:
            rows.append({
                "name": node.attrib['name'],
                "value": node.text.strip()
            })

        for row in rows:
            newItem = QTreeWidgetItem(self.treeMeta)
            setFontBold(newItem, column=0)
            newItem.setText(0, row['name'])
            newItem.setText(1, row['value'])


    def populateList(self):
        # IF this is an upload then cram some

        for key,op in self.qItem.opstore.iteritems():
            newItem = QTreeWidgetItem(self.treeFiles)
            newItem.setText(0, op.op)

            if op.direction == S3Operation.Direction.DOWN:
                destpath = op.abspath
            else:
                destpath = '/'.join(['s3://', op.bucket, op.fullkey])

            newItem.setText(1, destpath)

        if (len(self.treeFiles.children()) == 0):
            self.lblState.setText("No file operations queued. Nothing to do")
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        self.treeFiles.sortItems(1, Qt.AscendingOrder)