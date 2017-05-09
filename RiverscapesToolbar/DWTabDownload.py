from lib.async import ToolbarQueues

class DockWidgetTabDownload():

    def __init__(self, dockWidget):
        print "init DockWidgetTabDownload"
        self.Qs = ToolbarQueues()

        dockWidget.btnDownloadStart.clicked.connect(self.startWorker)
        dockWidget.btnDownloadPause.clicked.connect(self.stopWorker)

    def loadProject(dlg):
        print "Download loaded"

    def clearQueue(self):
        print "empty queue"

    def startWorker(self):
        self.Qs.startWorker()

    def stopWorker(self):
        self.Qs.stopWorker()


    def recalcState(self):
        """
        Here's where we update all the progress bars and the title card
        with "Queue (15%)"
        :return:
        """
        print "hi"
        # self.progOverall
        # self.progProject
        # self.progFile
        # setTabText(2, "New tab title");



