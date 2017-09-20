import os
from urlparse import urlparse

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal, QObject, QEvent
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
        self.initialized = False
        # Set up the user interface from Designer.
        self.setupUi(self)

        # Keep things on top
        self.setWindowTitle("Riverscapes Toolbar Settings")

        # Map settings keys to their respective text boxes
        self.settings = Settings()
        self.txtSettingMap = {
            'DataDir': self.txtDataRoot,
            'ProgramXMLUrl': self.txtProgramXMLUrl,
            'AWSAccessKeyID': self.txtAWSAccessKeyID,
            'AWSSecretAccessKey': self.txtAWSSecretAccessKey

        }
        self.lblMsgs.setStyleSheet('QLabel { color: red }')

        # Map functions to click events
        self.btnDataRootBrowse.clicked.connect(self.browseDataFolder)
        self.btnBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.btnBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.dlgReset)
        self.chkUseCustomCredentials.clicked.connect(self.AWSCheckBoxClick)

        self.chkS3Delete.clicked.connect(self.dlgApply)
        self.chkS3Force.clicked.connect(self.dlgApply)

        self.AWSCheckBoxClick()
        self.refreshUIState()

        # Map functions to click events
        self._eventfilter = EventFilter(self)
        for key, val in self.txtSettingMap.iteritems():
            # adjust for your QLineEdit
            val.installEventFilter(self._eventfilter)

        self.validate()

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

        if self.chkUseCustomCredentials.isChecked():
            if len(self.txtAWSAccessKeyID.text()) < 20:
                self.addMsg("ERROR: AWS Access Key ID is not valid.")
                valid = False
            if " " in self.txtAWSAccessKeyID.text():
                self.addMsg("ERROR: AWS Access Key ID cannot contain spaces.")
                valid = False

            if len(self.txtAWSSecretAccessKey.text()) < 40:
                self.addMsg("ERROR: AWS Secret Access Key is not valid.")
                valid = False
            if " " in self.txtAWSSecretAccessKey.text():
                self.addMsg("ERROR: AWS Secret Access Key cannot contain spaces.")
                valid = False

        self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(valid)
        self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(valid)

        return valid

    def AWSCheckBoxClick(self):
        """
        Toggle using local credentials
        :return:
        """

        if self.chkUseCustomCredentials.isChecked():
            self.groupBoxAWS.setEnabled(True)
        else:
            self.groupBoxAWS.setEnabled(False)

        self.dlgApply()

    def dlgApply(self):
        """
        Save all settings and close
        """
        if self.validate():
            settings = Settings()
            settings.saveSetting("accessError", False)
            settings.saveSetting("DataDir", self.txtDataRoot.text())
            settings.saveSetting("ProgramXMLUrl", self.txtProgramXMLUrl.text())

            # Refresh the programXML
            settings = Settings()
            if settings.getSetting("ProgramXMLUrl") != self.txtProgramXMLUrl.text():
                program = Program(force=True)
                if not program.valid:
                    self.addMsg("WARNING: Program XML could not be retrieved at this address")

            settings.saveSetting("AWSAccessKeyID", self.txtAWSAccessKeyID.text())
            settings.saveSetting("AWSSecretAccessKey", self.txtAWSSecretAccessKey.text())
            settings.saveSetting("AWSRegion", self.cmbAWSRegion.currentText())

            settings.saveSetting("UseCustomCredentials", self.chkUseCustomCredentials.isChecked())
            settings.saveSetting("S3Delete", self.chkS3Delete.isChecked())
            settings.saveSetting("S3Force", self.chkS3Force.isChecked())

            self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)

            settings.setAWSCredentials()

    def dlgReset(self):
        """
        Reset the form to sensible defaults
        """
        print "Reset"
        self.settings.resetAll()
        self.refreshUIState()

    def addMsg(self,msg):
        """
        Show a message in the label
        :param msg: 
        :return: 
        """
        if len(self.lblMsgs.text()) > 0:
            msg = "\n" + msg
        self.lblMsgs.setText(self.lblMsgs.text() + msg)


    def refreshUIState(self):
        """
        put the values in memory back into the text boxes
        :return: 
        """
        for key, val in self.txtSettingMap.iteritems():
            val.setText(self.settings.getSetting(key))

        self.chkUseCustomCredentials.setChecked(self.settings.getSetting("UseCustomCredentials"))
        self.chkS3Delete.setChecked(self.settings.getSetting("S3Delete"))
        self.chkS3Force.setChecked(self.settings.getSetting("S3Force"))


    def browseDataFolder(self):
        """
        Browse for a data folder
        :return: 
        """
        dataDir = QtGui.QFileDialog.getExistingDirectory(self, "Open a folder", os.path.expanduser("~"), QtGui.QFileDialog.ShowDirsOnly)
        self.txtDataRoot.setText(dataDir)
        self.validate()


class EventFilter(QObject):
    def __init__(self, dialog):
        super(EventFilter, self).__init__()
        self.dialog = dialog

    def eventFilter(self, widget, event):
        # FocusOut event
        if QEvent is not None and event.type() == QEvent.FocusOut:
            self.dialog.validate()

        # return False so that the widget will also handle the event
        # otherwise it won't focus out
        return False