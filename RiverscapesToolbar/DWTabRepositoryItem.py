from os import path
from functools import partial
import datetime

from program import Program
from lib.s3.walkers import s3GetFolderList, s3HeadData
from settings import Settings
from PyQt4.QtGui import QTreeWidgetItem, QIcon
from PyQt4.QtCore import Qt
from lib.treeitem import *
from lib.async import TreeLoadQueues

Qs = TreeLoadQueues()
Qs.startWorker()
settings = Settings()

class RepoTreeItem():

    # Some statics...
    LOADING = 'Loading...'

    def __init__(self, nItem=None, rtParent=None, pathArr=[], loadlevels=1, treectl=None):
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

        # Do we have the program XML yet? If not, go get it.
        self.program = Program()
        self.localdir = settings.getSetting('DataDir')

        self.nItem = nItem
        self.rtParent = rtParent

        # RootNode Stuff
        if not self.nItem:
            self.nItem = self.program.Hierarchy

        if not self.rtParent:
            self.qTreeWItem = QTreeWidgetItem(treectl)
        else:
            self.qTreeWItem = QTreeWidgetItem(self.rtParent.qTreeWItem)

        self.qTreeWItem.setText(0, self.LOADING)
        self.qTreeWItem.setHidden(True)

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
        self.loaded = False
        self.childrenloaded = False
        self.qTreeWItem.takeChildren()
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

        # if self.type != "product":
        #     self.createDummyChild()

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

        if not self.loaded:
            if self.type == 'product':
                self.name = self.nItem['node']['name']
            elif self.type == "group":
                self.name = self.nItem['node']['name']
                self.createDummyChild()
            elif self.type == 'collection':
                self.name = self.pathArr[-1]
                self.createDummyChild()
                try:
                    # try and find a better name than just the folder name (not always possible)
                    folderItem = next(
                        (d for d in self.nItem['node']['allows'] if d["folder"] == self.name and d['type'] == 'fixed'),
                        None)
                    if folderItem is not None:
                        self.name = folderItem['name']
                except Exception, e:
                    pass

        # Now add this onto a queue since it involves S3 operations
        self.qTreeWItem.setIcon(0, QIcon(qTreeIconStates.LOADING))
        Qs.load_q.put(self.recalcState);
        Qs.startWorker()

        self.loadChildren((loadlevels - 1))

    def recalcState(self):
        """
        All-important state function. This tells us a lot about what's new, what's old and what exists
        :return:
        """
        s3path = '/'.join(self.pathArr)
        localpath = path.join(self.localdir, path.sep.join(self.pathArr))

        if self.type == "product":
            self.qTreeWItem.setIcon(0, QIcon(qTreeIconStates.PRODUCT))
            head = s3HeadData(self.program.Bucket, s3path)
            self.local = path.isfile(localpath)
            self.remote = head is not None

            if self.local:
                setFontBold(self.qTreeWItem, column=0)
                setFontColor(self.qTreeWItem, "#444444", column=0)
            else:
                setFontColor(self.qTreeWItem, "#cccccc", column=0)

        elif self.type == 'group':
            self.qTreeWItem.setIcon(0, QIcon(qTreeIconStates.GROUP))
            # self.remote = s3Exists(self.program.Bucket, s3path)
            self.remote = True
            self.local = path.isdir(localpath)
            setFontColor(self.qTreeWItem, "#999999", column=0)


        elif self.type == 'collection':
            # With collections we've already done our checking with a directory list
            # So we assume the remote
            self.remote = True
            self.local = path.isdir(localpath)
            self.qTreeWItem.setIcon(0, QIcon())
            setFontColor(self.qTreeWItem, "#666666", column=0)

        self.qTreeWItem.setText(0, self.name)
        self.loadtime = datetime.datetime.now()

        # Walk back up the tree and hide things that have no value
        self.backwardCalc()
        self.loaded = True

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

    def createDummyChild(self):
        """
        We create a dummy node with the text  "Loading..." so that it looks like
        the item can be expanded, even if we don't know that
        :return:
        """
        self.qTreeWItem.takeChildren()
        self.dummychild = QTreeWidgetItem()
        self.dummychild.setText(0, self.LOADING)
        self.dummychild.setIcon(0, QIcon(qTreeIconStates.GROUP))
        self.qTreeWItem.addChild(self.dummychild)
        self.loaded = True


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
            # Now add this onto a queue since it involves S3 operations
            Qs.load_q.put(partial(self.loadchildrenworker, loadlevels));
            Qs.startWorker()

    def loadchildrenworker(self, loadlevels):
        self.qTreeWItem.takeChildren()
        for child in self.nItem['children']:
            # Add the leaf to the tree
            pathstr = '/'.join(self.pathArr) + '/' if len(self.pathArr) > 0 else ""
            type = child['node']['type']

            if type == 'product':
                # End of the line
                newpath = self.pathArr[:]
                newpath.append(child['node']['folder'])
                newpath.append(self.program.ProjectFile)
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
                for levelname in s3GetFolderList(self.program.Bucket, pathstr):
                    newpath = self.pathArr[:]
                    newpath.append(levelname)
                    newTreeItem = RepoTreeItem(child, self, newpath, loadlevels=loadlevels)
                    self.qTreeWItem.addChild(newTreeItem.qTreeWItem)

        self.childrenloaded = True

class qTreeIconStates:
    """
    Think of this like an enumeration for icons
    """

    LOCAL_MISSING = ":/plugins/RiverscapesToolbar/monitor_grey.png"
    LOCAL_OLDER = ":/plugins/RiverscapesToolbar/monitor_red.png"
    LOCAL_PRESENT = ":/plugins/RiverscapesToolbar/monitor_black.png"

    REMOTE_MISSING = ":/plugins/RiverscapesToolbar/cloud_grey.png"
    REMOTE_OLDER = ":/plugins/RiverscapesToolbar/cloud_red.png"
    REMOTE_PRESENT = ":/plugins/RiverscapesToolbar/cloud_black.png"

    GROUP = ":/plugins/RiverscapesToolbar/folder_light.png"
    COLLECTION = ":/plugins/RiverscapesToolbar/folder_medium.png"
    PRODUCT = ":/plugins/RiverscapesToolbar/project.png"

    LOADING = ":/plugins/RiverscapesToolbar/loading.png"