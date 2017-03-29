from lib.async import ToolbarQueues

class DockWidgetTabDownload():

    def __init__(self, dockWidget):
        print "init"
        ToolbarQueues()

    def loadProject(dlg):
        print "Download loaded"

    def startQueue(self):
        print "queue starting"

    def stopQueue(self):
        print "queue stopping"

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