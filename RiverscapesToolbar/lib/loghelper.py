from qgis.core import QgsMessageLog

class QGSLogger():

    @staticmethod
    def info(msg):
        QgsMessageLog.logMessage(msg, 'RiverscapesToolbar', QgsMessageLog.INFO)
    @staticmethod
    def error(msg):
        QgsMessageLog.logMessage(msg, 'RiverscapesToolbar', QgsMessageLog.CRITIAL)
    @staticmethod
    def warn(msg):
        QgsMessageLog.logMessage(msg, 'RiverscapesToolbar', QgsMessageLog.WARNING)