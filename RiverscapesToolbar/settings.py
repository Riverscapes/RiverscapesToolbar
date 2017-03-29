from PyQt4.QtCore import QSettings
from os import path
from lib.borg import Borg

# BASE is the name we want to use inside the settings keys
BASE="QGISRiverscapesToolbar"
# DEFAULT SETTINGS: We may need to externalize this somehow
_SETTINGS = {
    "DataDir": {
        "default": path.join(path.expanduser("~"), "RiverscapesData")
    },
    "ProgramXMLUrl": {
        "default": "https://raw.githubusercontent.com/Riverscapes/Program/master/Program/Riverscapes.xml"
    }
}

class Settings(Borg):
    """
    Read up on the Borg pattern if you don't already know it. Super useful
    """
    def __init__(self):
        Borg.__init__(self)

        print "Init Settings"
        s = QSettings()
        # Do a sanity check and reset anything that looks fishy
        for key in _SETTINGS.iterkeys():
            s.beginGroup(BASE)
            if key not in s.childKeys():
                self.resetDefault(key)
            else:
                val = self.getSetting(key)
                if len(val) == 0 or val is None:
                    self.resetDefault(key)
            s.endGroup()

    def resetAll(self):
        """
        rRset all items to their default values
        :return:
        """
        for key in _SETTINGS.iterkeys():
            self.resetDefault(key)

    def resetDefault(self, key):
        """
        Reset a single value to its default
        :param key:
        :return:
        """
        s = QSettings()
        s.beginGroup(BASE)
        if key in _SETTINGS and "default" in _SETTINGS[key]:
            s.setValue(key, _SETTINGS[key]['default'])
            _SETTINGS[key]['value'] = _SETTINGS[key]['default']
        s.endGroup()

    def getSetting(self, key):
        """
        Get one setting from the in-memory store and if not present then the settings file
        :return:
        """
        value = None
        if key in _SETTINGS and 'value' in _SETTINGS[key]:
            value = _SETTINGS[key]['value']
        else:
            s = QSettings()
            s.beginGroup(BASE)
            if key in s.childKeys():
                value = s.value(key)
                _SETTINGS[key]['value'] = value
            s.endGroup()
        return value

    def saveSetting(self, key, value):
        """
        Write or overwrite a setting. Update the in-memory store  at the same time
        :param name:
        :param settings:
        :return:
        """
        s = QSettings()
        s.beginGroup(BASE)
        # Set it in the file
        s.setValue(key, value)
        # Don't forget to save it back to memory
        _SETTINGS[key]['value'] = value
        s.endGroup()



