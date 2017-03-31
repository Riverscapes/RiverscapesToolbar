import xml.etree.ElementTree as ET
from PyQt4 import QtGui
from PyQt4.QtGui import QStandardItem, QMenu, QTreeWidgetItem, QMessageBox, QIcon, QPixmap, QDesktopServices
from PyQt4.QtCore import Qt, QUrl
from StringIO import StringIO
from lib.toc_management import *
from os import path, walk

class DockWidgetTabProject():

    treectl = None

    def __init__(self, dockWidget):
        print "init"
        DockWidgetTabProject.treectl = dockWidget.treeProject
        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)

        # Set up some connections for app events
        self.treectl.doubleClicked.connect(self.item_doubleClicked)
        self.treectl.customContextMenuRequested.connect(self.openMenu)
        dockWidget.btnLoadProject.clicked.connect(self.projectBrowserDlg)
        dockWidget.btnDEBUG.clicked.connect(self.loadDebug)



    def projectBrowserDlg(self):
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Open XML file", "", "XML File (*.xml);;GCD File (*.gcd);;All files (*)")
        self.projectLoad(filename)

    def loadDebug(self):
        """
        Quick and dirty hardcoded project loader so I can start work
        :return:
        """
        self.projectLoad('/Users/work/Projects/Riverscapes/Data/CRB/MiddleForkJohnDay/Network/VBET/project.rs.xml')

    @staticmethod
    def projectLoad(xmlPath):
        """ Constructor """
        if xmlPath is None or not path.isfile(xmlPath):
            msg = "..."
            q = QMessageBox(QMessageBox.Warning, "Could not find the project XML file", msg)
            q.setStandardButtons(QMessageBox.Ok)
            i = QIcon()
            i.addPixmap(QPixmap("..."), QIcon.Normal)
            q.setWindowIcon(i)
            q.exec_()
        else:
            rootItem = ProjectTreeItem(projectXMLfile=xmlPath)
            DockWidgetTabProject.treectl.expandToDepth(5)

    def addToMap(self, item):
        print "ADDING TO MAP::", item.data(0, Qt.UserRole)
        itemExt = path.splitext(item.data(0, Qt.UserRole)['filepath'])[1]
        if itemExt == '.shp':
            AddVectorLayer(item)
        else:
            AddRasterLayer(item)

    def item_doubleClicked(self, index):
        item = self.tree.selectedIndexes()[0]
        self.addToMap(item.model().itemFromIndex(index))

    def openMenu(self, position):
        """ Handle the contextual menu """
        item = self.treectl.selectedIndexes()[0]
        theData = item.data(Qt.UserRole)

        menu = QMenu()

        if (theData.type=="node"):
            addReceiver = lambda item=item: self.addToMap(item)
            findFolderReceiver = lambda item=theData: self.findFolder(item)

            addAction = menu.addAction("Add to Map", addReceiver)
            findAction = menu.addAction("Find Folder", findFolderReceiver)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def findFolder(self, rtItem):
        qurl = QUrl.fromLocalFile(path.join(ProjectTreeItem.localdir, path.sep.join(rtItem.pathArr[:-1])))
        QDesktopServices.openUrl(qurl)


class ProjectTreeItem():
    NODE_TYPE = "Node"
    REPEATER_TYPE = "Repeater"
    ENTITY_TYPE = "Entity"

    projectRootDir = None
    projectFilePath = None

    parserRootDir = None
    parserFilepath = None

    namespace = "{http://tempuri.org/ProjectDS.xsd}"

    projectDOM = None
    parserDOM = None

    @staticmethod
    def fetchProgramContext(projectXMLfile):
        """
        Get our program.xml and local Settings
        :return:
        """

        ProjectTreeItem.parserRootDir = path.join(path.dirname(__file__), "../XML/")
        ProjectTreeItem.projectFilePath = projectXMLfile
        ProjectTreeItem.projectRootDir = path.dirname(projectXMLfile)

        ProjectTreeItem.projectDOM = ProjectTreeItem._loadXMLFile(projectXMLfile)
        ProjectTreeItem.parserDOM = ProjectTreeItem._findTreeParser()

        # projectName = self.xmlProjectDoc.find("Project/name")

    def __init__(self, parseNode=None, projNode=None, rtParent=None, projectXMLfile=None):
        """
        Initialize a new RepoTreeItem
        :param nItem: nItem is the pseudo-json nested dictionary we get from program.py
        :param rtParent: rtParent is the RepoTreeItem (or root node) that owns this
        :param path: path is actually a list so we don't have to deal with slashes
        :param loadlevels:
        """

        # Do we have the program XML yet?
        if projectXMLfile:
            self.fetchProgramContext(projectXMLfile)

        self.parseNode = parseNode
        self.projNode = projNode
        self.rtParent = rtParent

        # RootNode Stuff. We've got to keep the parser in line and tracking the project node
        if not self.parseNode:
            self.parseNode = self.parserDOM.find('Node')
        if not self.projNode:
            self.projNode = self.projectDOM


        if not self.rtParent:
            self.qTreeWItem = QTreeWidgetItem(DockWidgetTabProject.treectl)
        else:
            self.qTreeWItem = QTreeWidgetItem(self.rtParent.qTreeWItem)

        # Set the data backwards so we can find this object later
        self.qTreeWItem.setData(0, Qt.UserRole, self)

        self.type = self.parseNode.tag
        self.depth = self._getDepth()
        self.load()

    def load(self, loadlevels=1):
        """
        Load a single item in the tree. This sets the name and color. Also gets the state of this item
        :param loadlevels:
        :return:
        """

        self.name = self._getLabel()
        self.qTreeWItem.setText(0, self.name)

        if self.type == 'Node':
            self.loadNode()
        elif self.type == "Repeater":
            self.loadRepeater()

        self.recalcState()
        self.loaded = True
        self.loadChildren()

    def recalcState(self):
        """
        All important state function. This tells us a lot about what's new, what's old and what exists
        :return:
        """
        self.qTreeWItem.setText(0, self.name)

        # Walk back up the tree and hide things that have no value
        self.backwardCalc()

    def backwardCalc(self):
        """
        This function traverses the list back up to the top hiding items that have visible children
        :return:
        """
        self.qTreeWItem.setHidden(False)

        # Now walk back up
        if self.rtParent:
            self.rtParent.backwardCalc()

    def loadNode(self):
        """
        Load a single node
        :return:
        """
        # Detect if this is an XML node element and reset the root Project node to this.
        entityType = self.parseNode.find('entity/type')
        entityXPath = self.parseNode.find('entity/xpath')
        newProjNode = self.projNode

        if entityXPath is not None:
            newProjNode = self.projNode.find(entityXPath.text)

        # This node might be a leaf. If so we need to get some meta dat
        if entityType is not None and entityXPath is not None:
            filepathNode = self.projNode.find(entityXPath.text)
            if filepathNode is not None:
                # normalize the slashes
                # filepath = re.sub('[\\\/]+', os.path.sep, filepathNode.text)
                # make it an absolute path
                filepath = os.path.join(self.xmlProjDir, filepathNode.text)
                self.filepath = filepath

            if entityXPath is not None:
                self.xpath = entityXPath.text
            symbologyNode = self.templateNode.find('entity/symbology')

            if symbologyNode is not None:
                self.symbology = symbologyNode.text

    def loadRepeater(self):

        # Remember, repeaters can only contain one "pattern" <Node>
        xPatternNode = self.parseNode.find("node")

        # If there is an Xpath then reset the base project node to that.
        xpath = self.parseNode.find("xpath")
        xNewProjList = []
        if xPatternNode is not None and xpath is not None:
            absoluteXPath = xpath.text[:1] == "/"

            # Should we search from the root or not.
            if absoluteXPath:
                xNewProjList = self.projectDOM.findall("." + xpath.text)
                newTreeItem = ProjectTreeItem(xNewProjList, self)
            else:
                xNewProjList = self.projNode.findall(xpath.text)
                newTreeItem = ProjectTreeItem(xNewProjList, self)

            self.qTreeWItem.addChild(newTreeItem.qTreeWItem)

        # for xProjChild in xNewProjList:
        #     self.LoadNode(newTreeItem, xPatternNode, xProjChild)


    def loadChildren(self):
        """
        Here's where we recurse down the tree to the end nodes.
        :param loadlevels:
        :param force:
        :return:
        """
        # self.group_layers = self.getTreeAncestry(newTreeItem)
        # Start by clearing out the previous children (this is a forced or first refresh)
        self.qTreeWItem.takeChildren()

        children = self.parseNode.find('Children')

        if children:
            for child in list(children):
                # Add the leaf to the tree
                newTreeItem = ProjectTreeItem(child, self)
                self.qTreeWItem.addChild(newTreeItem.qTreeWItem)

    def refreshAction(self):
        """
        When we right click and choose refresh
        :return:
        """
        print "refreshing"
        self.load()

    def _getLabel(self):
        """ Either use the liral text inside <label> or look it
            up in the project node if there's a <label xpath="/x/path">
        """
        label = "TITLE_NOT_FOUND"
        labelNode = self.parseNode.find("Label")
        if labelNode is not None:
            if "xpath" in labelNode.attrib:
                xpath = labelNode.attrib['xpath']
                label = self.projNode.find(xpath).text
            else:
                label = labelNode.text
        return label

    def _getDepth(self):
        """
        Find the root parent and count the depth of this object
        :return:
        """
        depth = 1
        currParent = self.rtParent
        # The first parent is not a RepoTreeItem so we can count them easily to get depth
        while isinstance(currParent, ProjectTreeItem):
            depth += 1
            currParent = currParent.rtParent
        return depth

    @staticmethod
    def getTreeAncestry(item):
        ancestry = []
        parent = item.parent()
        while parent is not None:
            ancestry.append(parent.text())
            parent = parent.parent()
        ancestry.reverse()
        return ancestry

    @staticmethod
    def _findTreeParser():
        """
        We need to figure out which kind of project it is. We do this by opening each parser we have
        and comparing the project types
        :return:
        """
        treeParser = None
        for subdir, dirs, files in walk(ProjectTreeItem.parserRootDir):
            xmlfiles = [filename for filename in files if filename.endswith(".xml")]
            for xmlfile in xmlfiles:
                filePath = path.join(subdir, xmlfile)
                candidate = ProjectTreeItem._loadXMLFile(filePath)
                testNode = candidate.find('ProjectType')
                projType = ProjectTreeItem.projectDOM.find("ProjectType")

                if testNode is not None and projType is not None and testNode.text == projType.text:
                    treeParser = candidate
                    continue
        return treeParser

    @staticmethod
    def _loadXMLFile(file):
        """
        Convenience method parse a filepath into a dom node and return the root
        :param file:
        :return:
        """
        with open(file, 'r') as myfile:
            data = myfile.read().replace('\n', '')
            it = ET.iterparse(StringIO(data))
            # strip all namespaces. This is an XML antipattern but it makes the project SOOOOO much
            # easier to work with.
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1]
            return it.root