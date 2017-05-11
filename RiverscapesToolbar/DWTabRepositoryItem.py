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
settings = Settings()

# Do we have the program XML yet? If not, go get it.
program = Program()

class RepoTreeItem():

    # Some statics...
    LOADING = 'Loading...'
    localrootdir = settings.getSetting('DataDir')

    class NState():
        INITIALIZED = 0
        LOADING = 1
        LOADED = 2
        LOAD_REQ = 3

    def __init__(self, nItem=None, rtParent=None, pathArr=[], treectl=None):
        """
        Initialize a new RepoTreeItem
        :param nItem: nItem is the pseudo-json nested dictionary we get from program.py
        :param rtParent: rtParent is the RepoTreeItem (or root node) that owns this
        :param path: path is actually a list so we don't have to deal with slashes
        """

        # Initial setup
        self.name = None
        self.state = self.NState.INITIALIZED
        self.childrenstate = self.NState.INITIALIZED

        self.icon = None
        self.loadtime = None
        self.dummyChild = None

        self.local = None
        self.remote = None
        self.localDateTime = None
        self.nowhere = True

        self.nItem = nItem
        self.rtParent = rtParent

        # RootNode Stuff
        if not self.nItem:
            self.nItem = program.Hierarchy

        if not self.rtParent:
            self.qTreeWItem = QTreeWidgetItem(treectl)
        else:
            self.qTreeWItem = QTreeWidgetItem(self.rtParent.qTreeWItem)

        # Set the data backwards so we can find this object later
        self.qTreeWItem.setData(0, Qt.UserRole, self)

        self.type = self.nItem['node']['type']
        self.depth = self._getDepth()
        self.pathArr = pathArr

        # TODO: This is a hack for now but it gets us over the hump
        if len(self.pathArr) == 0:
            self.pathArr = ["CRB"]

        self.reset()


    def getAbsProjRoot(self):
        return path.dirname(path.join(RepoTreeItem.localrootdir, path.sep.join(self.pathArr)))

    def getAbsProjFile(self):
        return path.dirname(path.join(RepoTreeItem.localrootdir, path.sep.join(self.pathArr)))

    def getRemoteS3Prefix(self):
        return path.dirname('/'.join(self.pathArr))


    def refreshAction(self):
        """
        When we right click and choose refresh
        :return:
        """
        print "Refreshing"
        self.reset()
        self.load()

    def reset(self):
        """
        Reset the node state
        :return:
        """
        self.state = self.NState.INITIALIZED
        self.childrenstate = self.NState.INITIALIZED
        self.name = ""
        self.loadtime = None
        self.nowhere = True
        self.local = None
        self.localDateTime = None
        self.remote = None
        self.icon = QIcon()
        self.color = "#000000"
        self.style = "regular"

        # Set some initial conditions to show we're doing something
        self.qTreeWItem.setText(0, self.LOADING)
        self.qTreeWItem.setHidden(self.nowhere)

        self.qTreeWItem.takeChildren()

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
        if self.state == self.NState.INITIALIZED:
            # There's no asynchronous loading for nodes so we jump straight to loaded
            self.state = self.NState.LOADED
            if self.type == 'product':
                self.name = self.nItem['node']['name']
                self.icon = QIcon(qTreeIconStates.PRODUCT)
                if self.local:
                    self.style = "bold"
                    self.color = "#444444"
                else:
                    self.style = "regular"
                    self.color = "#cccccc"

            elif self.type == "group":
                self.name = self.nItem['node']['name']
                self.icon = QIcon(qTreeIconStates.GROUP)
                self.dummyChild = self.createDummyChild()
                self.color = "#999999"

            elif self.type == 'collection':
                self.name = self.pathArr[-1]
                self.icon = QIcon()
                self.dummyChild = self.createDummyChild()
                # With collections we've already done our checking with a directory list
                # So we assume the remote exists
                self.color = "#666666"
                try:
                    # try and find a better name than just the folder name (not always possible)
                    folderItem = next(
                        (d for d in self.nItem['node']['allows'] if d["folder"] == self.name and d['type'] == 'fixed'),
                        None)
                    if folderItem is not None:
                        self.name = folderItem['name']
                except Exception, e:
                    pass

            self.formatNode()
            self.backwardCalc()

        if self.childrenstate == self.NState.INITIALIZED:
            self.childrenstate = self.NState.LOAD_REQ

        if self.type != 'product':
            Qs.queuePush(partial(self.loadChildren, (loadlevels - 1)));


    def backwardCalc(self):
        """
        This function traverses the list back up to the top hiding items that have visible children
        :return:
        """
        self.nowhere = not self.local and not self.remote

        if self.rtParent is None:
            self.nowhere = False

        # if self.type == "product":
        #     hide = True
        # else:
        # self.nowhere = not self.local and not self.remote
        # TODO: DECIDE IF THIS IS REALLY OK
        # if (self.qTreeWItem.childCount() > 0):
        #     print "hello"
        # allchildrenhidden = all([self.qTreeWItem.child(0).data(0, Qt.UserRole).nowhere for i in range(self.qTreeWItem.childCount())])
        # hide = allchildrenhidden

        if self.nowhere:
            setFontColor(self.qTreeWItem, "#FF0000", column=0)
            setFontItalic(self.qTreeWItem, column=0)

        self.qTreeWItem.setHidden(self.nowhere)

        # Now walk back up
        if self.rtParent:
            self.rtParent.backwardCalc()

    def createDummyChild(self):
        """
        We create a dummy node with the text  "Loading..." so that it looks like
        the item can be expanded, even if we don't know that
        :return:
        """
        dummychild = QTreeWidgetItem()
        dummychild.setText(0, self.LOADING)
        dummychild.setIcon(0, QIcon(qTreeIconStates.LOADING))
        self.qTreeWItem.addChild(dummychild)
        return dummychild


    def loadChildren(self, loadlevels=1):
        """
        Since this involves s3 lookup we have split it into its own method
        :param loadlevels: 
        :return: 
        """

        if loadlevels < 0:
            if self.childrenstate == self.NState.LOAD_REQ:
                self.childrenstate == self.NState.INITIALIZED
            return

        # Load levels is a very quick operation if there can't be children
        # or if we've reached the end of our load request chain
        if self.childrenstate != self.NState.LOAD_REQ:
            return

        self.childrenstate = self.NState.LOADING
        kids = []
        for child in self.nItem['children']:
            # Add the leaf to the tree
            pathstr = '/'.join(self.pathArr) + '/' if len(self.pathArr) > 0 else ""
            type = child['node']['type']

            if type == 'product':
                # End of the line
                newpath = self.pathArr[:]
                newpath.append(child['node']['folder'])
                newpath.append(program.ProjectFile)

                s3path = '/'.join(newpath)
                localpath = path.join(RepoTreeItem.localrootdir, path.sep.join(newpath))

                # Is it there?
                head = s3HeadData(program.Bucket, s3path)

                newItem = RepoTreeItem(child, self, newpath)
                newItem.local = path.isfile(localpath)
                newItem.remote = head is not None
                kids.append(newItem)

            elif type == 'group':
                newpath = self.pathArr[:]
                newpath.append(child['node']['folder'])
                DEBUG = child['node']['folder']
                newItem = RepoTreeItem(child, self, newpath)
                print "======== {} ===== {}".format(self.name, newItem.name)

                # self.remote = s3Exists(program.Bucket, s3path)
                newItem.remote = True
                localpath = path.join(RepoTreeItem.localrootdir, path.sep.join(newpath))
                newItem.local = path.isdir(localpath)
                kids.append(newItem)

            elif type == 'collection':
                # Unfortunately the only way to list collections is to go get them physically.
                for levelname in s3GetFolderList(program.Bucket, pathstr):
                    newpath = self.pathArr[:]
                    newpath.append(levelname)

                    newItem = RepoTreeItem(child, self, newpath)
                    newItem.remote = True
                    localpath = path.join(RepoTreeItem.localrootdir, path.sep.join(newpath))
                    newItem.local = path.isdir(localpath)
                    kids.append(newItem)

        # Do all the state recalc together so they all get visible at the same time
        [c.load(loadlevels) for c in kids]

        self.qTreeWItem.sortChildren(0, Qt.AscendingOrder)

        if self.dummyChild is not None:
            dummyind = self.qTreeWItem.indexOfChild(self.dummyChild)
            self.qTreeWItem.takeChild(dummyind)

        # Critical state check
        self.childrenstate = self.NState.LOADED


    def formatNode(self):
        # All nodes need a name and a datetime loaded
        self.loadtime = datetime.datetime.now()
        self.qTreeWItem.setIcon(0, self.icon)
        setFontColor(self.qTreeWItem, self.color, column=0)

        if self.style == "bold":
            setFontBold(self.qTreeWItem, column=0)

        elif self.style == "italic":
            setFontItalic(self.qTreeWItem, column=0)

        else:
            setFontRegular(self.qTreeWItem, column=0)
        self.qTreeWItem.setText(0, self.name)

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