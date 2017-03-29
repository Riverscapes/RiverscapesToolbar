from Queue import Queue
from PyQt4.QtCore import QThread, pyqtSignal, QObject, pyqtSlot
import traceback
from debug import InitDebug

class ToolbarQueuesBorg(object):
    _shared_state = {}
    _initdone = False

    def __init__(self):
        self.__dict__ = self._shared_state

class ToolbarQueues(ToolbarQueuesBorg):

    def __init__(self):
        super(ToolbarQueues, self).__init__()
        if not self._initdone:
            print "Init ToolbarQueues"
            self.project_q = Queue()
            self.project_complete_q = Queue()
            self.transfer_q = Queue()
            self.transfer_complete_q = Queue()

            # These are the thread processes that run the downloading processes
            self.worker = TransferWorker()
            self.worker_thread = QThread()
            self.worker.moveToThread(self.worker_thread)
            self.worker_thread.start()

            self.killrequested = False
            # Must be the last thing we do in init
            self._initdone = True

    def popProject(self):
        opstore = self.project_q.get()
        # opstore is a dict with { s3key: S3Operation }
        for key, val in opstore.iteritems():
            self.transfer_q.put((key, val))
        return opstore

    def listProjectQueue(self):
        return [opstore.S3Operation.conf['keyprefix'] for opstore in list(self.project_q.queue)]

    def listTransferQueue(self):
        return [transfer[0] for transfer in list(self.transfer_q.queue)]

    def stopWorker(self):
        self.worker.killRequested = True

class TransferWorker(QObject):
    """
    The worker class that will process our jobs
    """
    signalStatus = pyqtSignal(object)
    killrequested = False

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.currentProject = None

    def startProcessing(self):
        # Gives us breakpoints in a thread but only if we are in debug mode
        InitDebug()
        Qs = ToolbarQueues()
        try:
            print "QUEUE STARTED"
            while not self.killrequested:
                if Qs.transfer_q.qsize() > 0:
                    # If there's a file to download then download it.
                    transferitem = Qs.transfer_q.get()
                    self.signalStatus.emit({'status': 'Processing', 'item': transferitem})
                    transferitem.execute()
                    # Put it into the complete queue
                    Qs.transfer_complete_q.put(transferitem)
                    transferitem.task_done()

                else:
                    # Transfer queue is empty. Find something else to do:
                    if self.currentProject:
                        self.currentProject.task_done()
                        Qs.project_complete_q.put(self.currentProject)
                        self.currentProject = None
                    # Anything in the project Queue?
                    if Qs.project_q.qsize() > 0:
                        if Qs.project_q.qsize() == 0:
                            # Pop a project (if possible) into the download Queue
                            self.currentProject = Qs.popProject()
                    else:
                        self.signalStatus.emit({'status': 'Idle'})
            print "QUEUE STOPPED"
        except Exception, e:
            print "TransferWorkerThread Exception: {}".format(str(e))
            traceback.print_exc()


