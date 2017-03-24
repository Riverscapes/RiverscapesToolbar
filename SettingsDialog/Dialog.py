import os
from urlparse import urlparse

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal
import PyQt4.uic as uic
from settings import Settings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Dialog.ui'))

class SettingsDialog(QtGui.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(SettingsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.settings = Settings()
        # Keep things on top
        # self.window().setWindowFlags(self.window().windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Riverscapes Toolbar Settings")

        # Map settings keys to their respective text boxes
        self.settingMap = {
            'DataDir': self.txtDataRoot,
            'ProgramXMLUrl': self.txtProgramXMLUrl
        }

        # Map functions to click events
        self.btnDataRootBrowse.clicked.connect(self.browseDataFolder)
        self.btnBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.btnBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.dlgReset)

    def validate(self):
        """
        Make sure our settings are sane
        :return:
        """
        self.lblMsgs.text = ""
        valid = True

        # Is the data root a real value that corresponds to a folder?
        if len(self.txtDataRoot.text) == 0 or not os.path.isdir(self.txtDataRoot.text):
            self.addMsg("Base Dir is not a valid directory")
            valid = False

        # Is the URL a valid HREF or local file?
        parsed_url = urlparse.urlparse(self.txtProgramXMLUrl.text)

        if not bool(parsed_url.scheme) or str(parsed_url.path.split(".")[-1]).lower() != "xml":
            self.addMsg("Program XML is not a valid path")
            valid = False

        self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(valid)
        self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(valid)


    def dlgApply(self):
        """
        Save all settings and close
        """
        if self.validate():
            self.settings.save("DataDir", self.txtProgramXMLUrl.text)
            self.settings.save("ProgramXMLUrl", self.txtDataRoot.text)
            self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)

    def dlgReset(self):
        """
        """
        print "Reset"

    def addMsg(self,msg):
        if len(self.lblMsgs.text) > 0:
            msg = "\n" + msg
        self.lblMsgs.text = msg


    def browseDataFolder(self):
        dataDir = QtGui.QFileDialog.getExistingDirectory(self, "Open a folder", os.path.expanduser("~"), QtGui.QFileDialog.ShowDirsOnly)
        self.txtDataRoot.setText(dataDir)
        self.validate()