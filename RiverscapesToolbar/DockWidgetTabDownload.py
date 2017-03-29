from lib.async import ToolbarQueues

class DockWidgetTabDownload():

    def __init__(self, dockWidget):
        print "init DockWidgetTabDownload"
        self.Qs = ToolbarQueues()
        dockWidget.btnDownloadStart.clicked.connect(self.startQueue)
        dockWidget.btnDownloadPause.clicked.connect(self.stopQueue)

    def loadProject(dlg):
        print "Download loaded"

    def startQueue(self):
        print "queue starting"
        if not self.Qs.worker_thread.isRunning():
            self.Qs.worker_thread.start()
        self.Qs.worker.startProcessing()

    def stopQueue(self):
        print "queue stopping"
        self.Qs.worker.killRequested = True

    def resetQueue(self):
        if self.Qs.worker_thread.isRunning():
            self.Qs.worker_thread.terminate()
            self.Qs.worker_thread.wait()
            self.Qs.worker_thread.start()

    def clearQueue(self):
        self.stopQueue()
        print "empty queue"

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