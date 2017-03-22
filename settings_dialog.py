import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal, QSettings, Qt

BASE="RiverscapesToolbar"

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings_dialog_base.ui'))

# DEFAULT SETTINGS: We may need to externalize this somehow
SETTINGS = {
    "DataDir": {
        "default": "C:\\"
    },
    "ProgramXMLUrl": {
        "default": "https://raw.githubusercontent.com/Riverscapes/Program/master/Program/Riverscapes.xml"
    }
}


class SettingsDialog(QtGui.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(SettingsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.settings = ToolbarSettings()

        # Keep things on top
        self.window().setWindowFlags(self.window().windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Riverscapes Toolbar Settings")

        _SETTINGS['DataDir']['control'] = self.txtDataRoot
        _SETTINGS['DataDir']['control'] = self.txtProgramXMLUrl

        self.btnDataRootBrowse.clicked.connect(self.browseFolder)

        self.btnBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.btnBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.dlgApply)
        self.btnBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.dlgReset)

    def setfirstTime(self):
        """

        :return:
        """
        self.dlgReset()
        self.dlgApply()

    def validate(self):
        print "fine"

    def dlgApply(self):
        """
        Save all settings and close
        """
        if self.validate():
            saveSetting("DataDir", self.txtDataRoot.text)
            saveSetting("DataDir", self.txtDataRoot.text)
            self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
        else:
            self.btnBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
            self.btnBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)

    def dlgReset(self):
        """
        """

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    def browseFolder(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open XML file", "", "XML File (*.xml);;GCD File (*.gcd);;All files (*)")
        self.xmlLocation.setText(filename)
        self.validate()



class ToolbarSettings():

    def __init__(self):
        print "init"

    def initVals(self):
        """
        Make sure we have something set for every setting we need
        :return:
        """
        s = QSettings()
        for key, val in SETTINGS.iteritems():
            s.beginGroup(BASE)
            if key not in s.childKeys():
                value = s.setValue(key, val['default'])
            s.endGroup()

    def getSetting(self, key):
        """
        Get one setting
        :return:
        """
        value = None
        s = QSettings()
        s.beginGroup(BASE)
        if key in s.childKeys():
            value = s.value(key)
        s.endGroup()
        return value

    def saveSetting(self, key, value):
        """
        Write or overwrite a setting
        :param name:
        :param settings:
        :return:
        """
        s = QSettings()
        s.beginGroup(BASE)
        s.setValue(key, value)
        s.endGroup()
