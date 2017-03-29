from Queue import Queue
from PyQt4.QtCore import QThread, pyqtSignal
import traceback
from borg import Borg


class ToolbarQueues(Borg):

    def __init__(self):
        Borg.__init__(self)

        # These are the Queues we need to maintain
        self.project_q = Queue()
        self.project_complete_q = Queue()
        self.transfer_q = Queue()
        self.transfer_complete_q = Queue()

        # These are the thread processes that run the downloading processes
        self.worker_thread = TransferWorkerThread()
        self.worker_thread.start()

        # These are the ways we communicate back to the UI
        self.signalStatus = pyqtSignal(object)
        self.killRequested = False

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

    def stopThread(self):
        self.killRequested = True

    def startWorker(self):
        self.killRequested = False
        self.start()


class TransferWorkerThread(QThread):
    """
    The worker class that will process our jobs
    """
    def run(self):
        try:
            count = 0
            Qs = ToolbarQueues()
            currentProject = None

            while not Qs.killRequested:

                if Qs.transefer_q.qsize() > 0:
                    # If there's a file to download then download it.
                    transferitem = Qs.transfer_q.get()
                    Qs.signalStatus.emit({'status': 'Processing', 'item': transferitem})
                    transferitem.execute()
                    Qs.project_complete_q
                    transferitem.task_done()

                else:
                    # Transfer queue is empty. Find something else to do:
                    if currentProject:
                        currentProject.task_done()
                        currentProject = None
                    # Anything in the project Queue?
                    if Qs.project_q.qsize() > 0:
                        if Qs.project_q.qsize() == 0:
                            # Pop a project (if possible) into the download Queue
                            currentProject = Qs.popProject()
                    else:
                        Qs.signalStatus.emit({'status': 'Idle'})
        except Exception, e:
            print "TransferWorkerThread Exception: {}".format(str(e))
            traceback.print_exc()
