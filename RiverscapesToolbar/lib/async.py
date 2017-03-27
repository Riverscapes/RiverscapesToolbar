# We need a way to run asynchronous code so the UI stays responsive when we're doing things:
import sys
from PyQt4 import QtCore
from PyQt4 import QtGui


class RunObjectContainer(QtCore.QObject):
    #temporarily holds references so objects don't get garbage collected
    def __init__(self):
        self._container = set()

    def add(self, obj):
        self._container.add(obj)

    @QtCore.pyqtSlot(object)
    def discard(self, obj):
        self._container.discard(obj)

container = RunObjectContainer()

class RunObject(QtCore.QObject):
    run_complete = QtCore.pyqtSignal(object)
    def __init__(self, parent=None,f=None):
        super(RunObject, self).__init__(parent)
        self._f = f

    @QtCore.pyqtSlot()
    def run(self):
        self._f()
        self.run_complete.emit(self)


main_thread = None
worker_thread = QtCore.QThread()


def run_on_thread(thread_to_use, f):
    run_obj = RunObject(f=f)
    container.add(run_obj)
    run_obj.run_complete.connect(container.discard)
    if QtCore.QThread.currentThread() != thread_to_use:
        run_obj.moveToThread(thread_to_use)
    QtCore.QMetaObject.invokeMethod(run_obj, 'run', QtCore.Qt.QueuedConnection)

def print_run_on(msg):
    if QtCore.QThread.currentThread() == main_thread:
        print(msg + " -- run on main thread")
    elif QtCore.QThread.currentThread() == worker_thread:
        print(msg + " -- run on worker thread")
    else:
        print("error " + msg + " -- run on unkown thread")
        raise Exception(msg + " -- run on unkown thread")


class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
    def initUI(self):
        self.button = QtGui.QPushButton('Test', self)
        self.button.clicked.connect(self.handleButton)
        self.show()

    def handleButton(self):
        run_on_thread(main_thread, lambda: print_run_on("main_thread"))
        run_on_thread(worker_thread, lambda: print_run_on("worker_thread"))

        def n():
            a = "yoyoyo"
            print_run_on("running function n on thread ")
            run_on_thread(main_thread, lambda: print_run_on("calling nested from n "))
            run_on_thread(worker_thread, lambda: print_run_on("a is " + a))
        run_on_thread(worker_thread, n)

        print("end of handleButton")

def gui_main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    worker_thread.start()
    global main_thread
    main_thread = app.thread()
    sys.exit(app.exec_())

if __name__ == '__main__':
    gui_main()