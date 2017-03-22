import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal

from PyQt4.QtCore import QSettings

BASE="RiverscapesToolbar"

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings_dialog_base.ui'))

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

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()



def getSetting(key):
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

def saveSetting(key, value):
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
