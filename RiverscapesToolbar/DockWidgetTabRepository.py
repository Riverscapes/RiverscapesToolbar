from lib.program import ProgramXML
from lib.s3.walkers import s3GetFolderList, s3Exists, s3HeadData
import datetime
from settings import Settings
from PyQt4.QtGui import QMenu, QTreeWidgetItem, QDesktopServices, QIcon
from PyQt4.QtCore import Qt, QUrl
from os import path
from lib.treehelper import *
from DockWidgetTabProject import DockWidgetTabProject

class DockWidgetTabRepository():

    treectl = None

    def __init__(self, dockWidget):
        # used to be:
        # def __init__(self, xmlPath, treeControl, parent=None):
        # Connect up our buttons to functions
        self.dockwidget = dockWidget

        # Set as static so we can find it.
        DockWidgetTabRepository.treectl = dockWidget.treeRepository
        self.treectl.setAlternatingRowColors(True)
        self.treectl.setContextMenuPolicy(Qt.CustomContextMenu)

        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)

        self.treectl.customContextMenuRequested.connect(self.openMenu)
        self.treectl.doubleClicked.connect(self.item_doubleClicked)
        self.treectl.itemExpanded.connect(self.expandItem)

        dockWidget.btnRefresh.clicked.connect(self.refreshRoot)
        self.refreshRoot()

    def expandItem(self, item):
        """
        Reload this
        :param item:
        :return:
        """
        item.data(0, Qt.UserRole).loadChildren()

    def refreshRoot(self):
        """
        Refresh the main dialog
        :return:
        """
        self.dockwidget.btnRefresh.setText("Loading...")
        self.dockwidget.btnRefresh.setEnabled(False)

        rootItem = RepoTreeItem(loadlevels = 2)
        self.treectl.expandToDepth(0)

        self.dockwidget.btnRefresh.setEnabled(True)
        self.dockwidget.btnRefresh.setText("Refresh")

    def item_doubleClicked(self, index):
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        if theData.type=="product" and theData.local:
            self.openProject(theData)


    def openMenu(self, pt):
        """ Handle the contextual menu """
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        menu = QMenu()
        refreshReceiver = lambda item=theData: item.refreshAction()

        if (theData.type=="product"):
            openReceiver = lambda item=theData: self.openProject(item)
            downloadReceiver = lambda item=theData: self.addProjectToDownloadQueue(item)
            uploadReceiver = lambda item=theData: self.addProjectToUploadQueue(item)
            findFolderReceiver = lambda item=theData: self.findFolder(item)

            openAction = menu.addAction("Open Project", openReceiver)
            menu.addSeparator()
            downAction = menu.addAction("Download Project", downloadReceiver)
            uploAction = menu.addAction("Upload Project", uploadReceiver)
            menu.addSeparator()
            refreshAction = menu.addAction("Refresh", refreshReceiver)
            findAction = menu.addAction("Find Folder", findFolderReceiver)

            # The actions are available if the projects are available locally or otherwise
            openAction.setEnabled(theData.local)
            downAction.setEnabled(theData.remote)
            uploAction.setEnabled(theData.local)
            findAction.setEnabled(theData.local)

        else:
            dwnQueueReceiver = lambda item=theData: self.openProject(item)
            queueContainerAction = menu.addAction("Add projects to Download Queue", dwnQueueReceiver)
            refreshAction = menu.addAction("Refresh", refreshReceiver)

            queueContainerAction.setEnabled(True)

        menu.exec_(self.treectl.mapToGlobal(pt))

    def addProjectToDownloadQueue(self, rtItem):
        print "Adding to download Queue: " + '/'.join(rtItem.pathArr)

    def addProjectToUploadQueue(self, rtItem):
        print "Adding to Upload Queue: " + '/'.join(rtItem.pathArr)

    def findFolder(self, rtItem):
        qurl = QUrl.fromLocalFile(path.join(RepoTreeItem.localdir, path.sep.join(rtItem.pathArr[:-1])))
        QDesktopServices.openUrl(qurl)

    def openProject(self, rtItem):
        print "OPEN THE PROJECT"
        localpath = path.join(RepoTreeItem.localdir, path.sep.join(rtItem.pathArr))
        # Switch to the project tab
        self.dockwidget.tabWidget.setCurrentIndex(self.dockwidget.PROJECT_TAB)
        DockWidgetTabProject.projectLoad(localpath)


class RepoTreeItem():

    # Some statics...
    LOADING = 'Loading...'
    program = None
    localdir = None

    @staticmethod
    def fetchProgramContext():
        """
        Get our program.xml and local Settings
        :return:
        """
        settings = Settings()
        RepoTreeItem.program = ProgramXML(settings.getSetting('ProgramXMLUrl'))
        RepoTreeItem.localdir = settings.getSetting('DataDir')

    def __init__(self, nItem=None, rtParent=None, pathArr=[], loadlevels=1):
        """
        Initialize a new RepoTreeItem
        :param nItem: nItem is the pseudo-json nested dictionary we get from program.py
        :param rtParent: rtParent is the RepoTreeItem (or root node) that owns this
        :param path: path is actually a list so we don't have to deal with slashes
        :param loadlevels:
        """

        # Initial setup
        self.name = ""
        self.loaded = False
        self.childrenloaded = False

        self.loadtime = None

        self.local = None
        self.localDateTime = None
        self.remote = None
        self.queued = None

        # Do we have the program XML yet?
        if not RepoTreeItem.program or not RepoTreeItem.localdir:
            self.fetchProgramContext()

        self.nItem = nItem
        self.rtParent = rtParent

        # RootNode Stuff
        if not self.nItem:
            self.nItem = RepoTreeItem.program.Hierarchy

        if not self.rtParent:
            self.qTreeWItem = QTreeWidgetItem(DockWidgetTabRepository.treectl)
        else:
            self.qTreeWItem = QTreeWidgetItem(self.rtParent.qTreeWItem)

        # Set the data backwards so we can find this object later
        self.qTreeWItem.setData(0, Qt.UserRole, self)

        self.type = self.nItem['node']['type']
        self.depth = self._getDepth()
        self.pathArr = pathArr
        self.reset()

        # TODO: This is a hack for now but it gets us over the hump
        if len(self.pathArr) == 0:
            self.pathArr = ["CRB"]

        self.load(loadlevels)

    def refreshAction(self):
        """
        When we right click and choose refresh
        :return:
        """
        print "refreshing"
        self.reset()
        self.load()

    def reset(self):
        """
        Reset the node state
        :return:
        """
        self.name = ""
        self.loaded = False
        self.childrenloaded = False

        self.loadtime = None

        self.local = None
        self.localDateTime = None
        self.remote = None
        self.queued = None

        self.qTreeWItem.setText(0, self.LOADING)
        if self.type != "product":
            self.createDummyChild()

    def _getDepth(self):
        """
        Find the root parent and count the depth of this object
        :return:
        """
        depth = 1
        currParent = self.rtParent
        # The first parent is not a RepoTreeItem so we can count them easily to get depth
        while isinstance(currParent, RepoTreeItem):
            depth += 1
            currParent = currParent.rtParent
        return depth

    def load(self, loadlevels=1):
        """
        Load a single item in the tree. This sets the name and color. Also gets the state of this item
        :param loadlevels:
        :return:
        """

        if self.type == 'product':
            self.name = self.nItem['node']['name']
        elif self.type == "group":
            self.name = self.nItem['node']['name']
        elif self.type == 'collection':
            self.name = self.pathArr[-1]
            try:
                # try and find a better name than just the folder name (not always possible)
                folderItem = next(
                    (d for d in self.nItem['node']['allows'] if d["folder"] == self.name and d['type'] == 'fixed'),
                    None)
                if folderItem is not None:
                    self.name = folderItem['name']
            except Exception, e:
                pass

        self.recalcState()
        self.loaded = True
        self.loadChildren((loadlevels - 1))

    def recalcState(self):
        """
        All important state function. This tells us a lot about what's new, what's old and what exists
        :return:
        """
        s3path = '/'.join(self.pathArr)
        localpath = path.join(RepoTreeItem.localdir, path.sep.join(self.pathArr))

        if self.type == "product":
            self.qTreeWItem.setIcon(0, QIcon(qTreeIconStates.PRODUCT))
            head = s3HeadData(RepoTreeItem.program.Bucket, s3path)
            self.local = path.isfile(localpath)
            self.remote = head is not None

            if self.local:
                setFontBold(self.qTreeWItem, column=0)
                setFontColor(self.qTreeWItem, "#444444", column=0)
            else:
                setFontColor(self.qTreeWItem, "#cccccc", column=0)

        elif self.type == 'group':
            self.qTreeWItem.setIcon(0, QIcon(qTreeIconStates.GROUP))
            # self.remote = s3Exists(RepoTreeItem.program.Bucket, s3path)
            self.remote = True
            self.local = path.isdir(localpath)
            setFontColor(self.qTreeWItem, "#999999", column=0)


        elif self.type == 'collection':
            # With collections we've already done our checking with a directory list
            # So we assume the remote
            self.remote = True
            self.local = path.isdir(localpath)
            setFontColor(self.qTreeWItem, "#666666", column=0)

        self.qTreeWItem.setText(0, self.name)
        self.loadtime = datetime.datetime.now()

        # Walk back up the tree and hide things that have no value
        self.backwardCalc()

    def createDummyChild(self):
        """
        We create a dummy node with the text  "Loading..." so that it looks like
        the item can be expanded, even if we don't know that
        :return:
        """
        self.qTreeWItem.takeChildren()
        dummy = QTreeWidgetItem()
        dummy.setText(0, self.LOADING)
        dummy.setIcon(0, QIcon(qTreeIconStates.GROUP))
        self.qTreeWItem.addChild(dummy)

    def backwardCalc(self):
        """
        This function traverses the list back up to the top hiding items that have visible children
        :return:
        """
        hide = False
        if self.type == "product":
            hide = not self.local and not self.remote
        else:
            hide = not self.local and not self.remote
            # TODO: DECIDE IF THIS IS REALLY OK
            # allchildrenhidden = all([self.qTreeWItem.child(i).isHidden() for i in range(self.qTreeWItem.childCount())])
            # hide = self.qTreeWItem.childCount() == 0 or allchildrenhidden
        self.qTreeWItem.setHidden(hide)

        # Now walk back up
        if self.rtParent:
            self.rtParent.backwardCalc()

    def loadChildren(self, loadlevels=1, force=False):
        """
        Here's where we recurse down the tree to the end nodes.
        :param loadlevels:
        :param force:
        :return:
        """
        # This is a hard rule. Children have no products.
        if self.type == 'product':
            return
        # Stop loading past a certain level
        if loadlevels < 0:
            return

        if self.childrenloaded and not force:
            # Just recalculate the children. Don't reload anything
            for i in range(self.qTreeWItem.childCount()):
                if self.qTreeWItem.isExpanded():
                    self.qTreeWItem.child(i).data(0, Qt.UserRole).load()
        else:
            # Start by clearing out the previous children (this is a forced or first refresh)
            self.qTreeWItem.takeChildren()

            for child in self.nItem['children']:
                # Add the leaf to the tree
                pathstr = '/'.join(self.pathArr) + '/' if len(self.pathArr) > 0 else ""
                type = child['node']['type']

                if type == 'product':
                    # End of the line
                    newpath = self.pathArr[:]
                    newpath.append(child['node']['folder'])
                    newpath.append(RepoTreeItem.program.ProjectFile)
                    newTreeItem = RepoTreeItem(child, self, newpath, loadlevels=loadlevels)
                    self.qTreeWItem.addChild(newTreeItem.qTreeWItem)

                elif type == 'group':
                    newpath = self.pathArr[:]
                    newpath.append(child['node']['folder'])
                    newTreeItem = RepoTreeItem(child, self, newpath, loadlevels=loadlevels)
                    self.qTreeWItem.addChild(newTreeItem.qTreeWItem)

                elif type == 'collection':
                    # Unfortunately the only way to list collections is to go get them physically.
                    # TODO: THIS NEEDS TO INCORPORATE LOCAL AS WELL.
                    for levelname in s3GetFolderList(RepoTreeItem.program.Bucket, pathstr):
                        newpath = self.pathArr[:]
                        newpath.append(levelname)
                        newTreeItem = RepoTreeItem(child, self, newpath, loadlevels=loadlevels)
                        self.qTreeWItem.addChild(newTreeItem.qTreeWItem)

            self.childrenloaded = True


class qTreeIconStates:
    # Think of this like an enumeration for icons
    LOCAL_MISSING = ":/symbolizers/RiverscapesToolbar/monitor_grey.png"
    LOCAL_OLDER = ":/symbolizers/RiverscapesToolbar/monitor_red.png"
    LOCAL_PRESENT = ":/symbolizers/RiverscapesToolbar/monitor_black.png"

    REMOTE_MISSING = ":/symbolizers/RiverscapesToolbar/cloud_grey.png"
    REMOTE_OLDER = ":/symbolizers/RiverscapesToolbar/cloud_red.png"
    REMOTE_PRESENT = ":/symbolizers/RiverscapesToolbar/cloud_black.png"

    GROUP = ":/symbolizers/RiverscapesToolbar/folder_light.png"
    COLLECTION = ":/symbolizers/RiverscapesToolbar/folder_medium.png"
    PRODUCT = ":/symbolizers/RiverscapesToolbar/project.png"

    LOADING = ":/symbolizers/RiverscapesToolbar/loading.png"