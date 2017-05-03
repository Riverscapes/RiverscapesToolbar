import xml.etree.ElementTree as ET
from PyQt4 import QtGui
from settings import Settings
from PyQt4.QtGui import QStandardItem, QMenu, QTreeWidgetItem, QMessageBox, QIcon, QPixmap, QDesktopServices
from PyQt4.QtCore import Qt, QUrl
from StringIO import StringIO
from tocmanage import AddGroup, AddRasterLayer, AddVectorLayer
from symbology.symbology import Symbology
from os import path, walk

class DockWidgetTabProject():

    treectl = None

    def __init__(self, dockWidget):
        print "init"
        DockWidgetTabProject.treectl = dockWidget.treeProject
        self.widget = dockWidget
        self.treectl.setColumnCount(1)
        self.treectl.setHeaderHidden(True)
        # Load the plugins
        self.symbology = Symbology()
        # Set up some connections for app events
        self.treectl.doubleClicked.connect(self.item_doubleClicked)
        self.treectl.customContextMenuRequested.connect(self.openMenu)
        dockWidget.btnLoadProject.clicked.connect(self.projectBrowserDlg)
        dockWidget.btnDEBUG.clicked.connect(self.loadDebug)


    def projectBrowserDlg(self):
        settings = Settings()
        filename = QtGui.QFileDialog.getExistingDirectory(self.widget, "Open a project", settings.getSetting('DataDir'))
        self.projectLoad(filename)

    def loadDebug(self):
        """
        Quick and dirty hardcoded project loader so I can start work
        :return:
        """
        # Start by clearing out the previous children (this is a forced or first refresh)
        QTreeWidgetItem(DockWidgetTabProject.treectl).takeChildren()
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
        :param parseNode: The business logic to decide what to do with this
        :param projNode: The actual project node we're working with.
        :param rtParent: rtParent is the RepoTreeItem (or root node) that owns this
        :param projectXMLfile: If we're loading from a file this is what you pass in
        """

        # Do we have the program XML yet?
        if projectXMLfile:
            self.fetchProgramContext(projectXMLfile)

        self.parseNode = parseNode
        self.projNode = projNode
        self.rtParent = rtParent
        self.xpath = None

        # RootNode Stuff. We've got to keep the parser in line and tracking the project node
        if self.parseNode is None:
            self.parseNode = self.parserDOM.find('Node')
        if self.projNode is None:
            self.projNode = self.projectDOM

        if not self.rtParent:
            self.qTreeWItem = QTreeWidgetItem(DockWidgetTabProject.treectl)
            self.qTreeWItem.takeChildren()
        else:
            self.qTreeWItem = QTreeWidgetItem(self.rtParent.qTreeWItem)

        # This node could be referring to another.
        # refNode could be the projNode or it could be the lookup
        self.refNode = self.projNode

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

        if self.type == 'Node':
            self.loadNode()
            self.loadChildren()
        elif self.type == "Repeater":
            self.loadRepeater()

        self.name = self._getLabel()
        self.recalcState()
        self.loaded = True

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

    @staticmethod
    def getAttr(node, lookupstr):
        output = None
        if lookupstr in node.attrib:
            output = node.attrib[lookupstr]
        return output

    def loadNode(self):
        """
        Load a single node
        :return:
        """
        # Detect if this is an XML node element and reset the root Project node to this.
        nodeType = ProjectTreeItem.getAttr(self.parseNode, 'type')

        # the Project node can be further updated by an xpath attribute
        nodeXPath = ProjectTreeItem.getAttr(self.parseNode, 'xpath')
        if nodeXPath is not None:
            self.xpath = nodeXPath
            self.projNode = self.projNode.find(nodeXPath)
            self.refNode = self.projNode

        # This node might be referring to another one. Go look that up
        refID = ProjectTreeItem.getAttr(self.projNode, 'ref')
        if refID is not None:
            # We have a ref attribute. Go find it.
            self.refNode = self.projectDOM.find(".//*[@id='{0}']".format(refID))

        # This node might be a leaf. If so we need to get some meta dat
        if nodeType is not None:
            filepathNode = self.refNode.find('Path')
            if filepathNode is not None:
                # normalize the slashes
                # filepath = re.sub('[\\\/]+', os.path.sep, filepathNode.text)
                # make it an absolute path
                filepath = path.join(ProjectTreeItem.projectRootDir, filepathNode.text)
                self.filepath = filepath

            symbologyNode = ProjectTreeItem.getAttr(self.parseNode, 'symbology')
            if symbologyNode is not None:
                self.symbology = symbologyNode


    def loadRepeater(self):

        # Remember, repeaters can only contain one "pattern" <Node>
        xPatternNode = self.parseNode.find("Node")

        # If there is an Xpath then reset the base project node to that.
        xpath = ProjectTreeItem.getAttr(self.parseNode, 'xpath')

        xNewProjList = []
        if xPatternNode is not None and xpath is not None:
            absoluteXPath = xpath[:1] == "/"

            # Should we search from the root or not.
            if absoluteXPath:
                xNewProjList = self.projectDOM.findall("." + xpath)
            else:
                xNewProjList = self.projNode.findall(xpath)

            for xProjChild in xNewProjList:
                newTreeItem = ProjectTreeItem(xPatternNode, xProjChild, self)
                self.qTreeWItem.addChild(newTreeItem.qTreeWItem)


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

        for xParseChild in self.parseNode.findall('Children/*'):
            # Add the leaf to the tree
            newTreeItem = ProjectTreeItem(xParseChild, self.projNode, self)
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
        labellit = ProjectTreeItem.getAttr(self.parseNode, 'label')
        labelxpath = ProjectTreeItem.getAttr(self.parseNode, 'xpathlabel')

        if labelxpath is not None:
            labelNode = self.refNode.find(labelxpath)
            if labelNode is not None:
                label = labelNode.text
            else:
                print "thing"
        elif labellit is not None:
            label = labellit
        # return "{0} - ({1})".format(label, self.type)
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