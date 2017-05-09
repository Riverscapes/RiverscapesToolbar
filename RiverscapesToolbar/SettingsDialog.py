import os
from urlparse import urlparse

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal
import PyQt4.uic as uic
from settings import Settings
from program import Program

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'SettingsDialog.ui'))

class SettingsDialog(QtGui.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(SettingsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)

        # Keep things on top
        self.setWindowTitle("Riverscapes Toolbar Settings")

        # Map settings keys to their respective text boxes
        self.settings = Settings()
        self.settingMap = {
            'DataDir': self.txtDataRoot,
            'ProgramXMLUrl': self.txtProgramXMLUrl
        }
        self.lblMsgs.setStyleSheet('QLabel { color: red }')

        # Map functions to click events
        self.btnDataRootBrowse.clicked.connect(self.browseDataFolder)
        self.btnBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.btnBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.dlgReset)

        # Map functions to click events
        for key, val in self.settingMap.iteritems():
            val.textChanged.connect(self.validate)

        self.refreshTextBoxes()

    def validate(self):
        """
        Make sure our settings are sane
        :return:
        """
        print "validating"
        self.lblMsgs.setText("")
        valid = True

        # Is the data root a real value that corresponds to a folder?
        if len(self.txtDataRoot.text()) == 0 or not os.path.isdir(self.txtDataRoot.text()):
            self.addMsg("ERROR: Data Root must be an existing directory.")
            valid = False

        # Is the URL a valid HREF or local file?
        parsed_url = urlparse(self.txtProgramXMLUrl.text())

        if not bool(parsed_url.scheme) or str(parsed_url.path.split(".")[-1]).lower() != "xml":
            self.addMsg("ERROR: Program XML is not a valid url (http://something.com/a/b/c/Program.xml)")
            valid = False

        self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(valid)
        self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(valid)

        return valid

    def dlgApply(self):
        """
        Save all settings and close
        """
        if self.validate():

            settings = Settings()
            settings.saveSetting("DataDir", self.txtDataRoot.text())
            settings.saveSetting("ProgramXMLUrl", self.txtProgramXMLUrl.text())

            self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)

            # Refresh the programXML
            program = Program(force=True)

    def dlgReset(self):
        """
        Reset the form to sensible defaults
        """
        print "Reset"
        self.settings.resetAll()
        self.refreshTextBoxes()

    def addMsg(self,msg):
        """
        Show a message in the label
        :param msg: 
        :return: 
        """
        if len(self.lblMsgs.text()) > 0:
            msg = "\n" + msg
        self.lblMsgs.setText(self.lblMsgs.text() + msg)


    def refreshTextBoxes(self):
        """
        put the values in memory back into the text boxes
        :return: 
        """
        for key, val in self.settingMap.iteritems():
            val.setText(self.settings.getSetting(key))


    def browseDataFolder(self):
        """
        Browse for a data folder
        :return: 
        """
        dataDir = QtGui.QFileDialog.getExistingDirectory(self, "Open a folder", os.path.expanduser("~"), QtGui.QFileDialog.ShowDirsOnly)
        self.txtDataRoot.setText(dataDir)
        self.validate()