from os import path, walk
from StringIO import StringIO
from treehelper import *
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtCore import Qt
import xml.etree.ElementTree as ET


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

        ProjectTreeItem.parserRootDir = path.join(path.dirname(__file__), "../../XML/")
        ProjectTreeItem.projectFilePath = projectXMLfile
        ProjectTreeItem.projectRootDir = path.dirname(projectXMLfile)

        ProjectTreeItem.projectDOM = ProjectTreeItem._loadXMLFile(projectXMLfile)
        ProjectTreeItem.parserDOM = ProjectTreeItem._findTreeParser()

        # projectName = self.xmlProjectDoc.find("Project/name")

    def __init__(self, parseNode=None, projNode=None, rtParent=None, projectXMLfile=None, treectl=None):
        """        
        :param parseNode: The business logic to decide what to do with this
        :param projNode: The actual project node we're working with.
        :param rtParent: rtParent is the RepoTreeItem (or root node) that owns this
        :param projectXMLfile: If we're loading from a file this is what you pass in
        """

        # Do we have the program XML yet?
        if projectXMLfile:
            self.fetchProgramContext(projectXMLfile)

        self.name = ""
        self.parseNode = parseNode
        self.projNode = projNode
        self.rtParent = rtParent
        self.xpath = None
        self.maptype = None
        self.symbology = None

        # RootNode Stuff. We've got to keep the parser in line and tracking the project node
        if self.parseNode is None:
            self.parseNode = self.parserDOM.find('Node')
        if self.projNode is None:
            self.projNode = self.projectDOM

        if not self.rtParent:
            self.qTreeWItem = QTreeWidgetItem(treectl)
        else:
            self.qTreeWItem = QTreeWidgetItem(self.rtParent.qTreeWItem)

        self.qTreeWItem.takeChildren()

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
        # Start by clearing out the previous children (this is a forced or first refresh)

        if self.type == 'Node':
            self.loadNode()
            self.loadChildren()
        elif self.type == "Repeater":
            self.loadRepeater()

        self.name = self.getLabel()
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
            self.maptype = nodeType
            setFontBold(self.qTreeWItem, column=0)
            setFontColor(self.qTreeWItem, "#444444", column=0)

            filepathNode = self.refNode.find('Path')
            if filepathNode is not None:
                # normalize the slashes
                # filepath = re.sub('[\\\/]+', os.path.sep, filepathNode.text)
                # make it an absolute path
                filepath = path.join(ProjectTreeItem.projectRootDir, filepathNode.text)
                self.filepath = filepath

            self.symbology = ProjectTreeItem.getAttr(self.parseNode, 'symbology')


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
        # Start by clearing out the previous children (this is a forced or first refresh)

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

    def getLabel(self):
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

    def getTreeAncestry(self):
        """
        Returns a really simple ancestry line so we can 
        build a map layer later
        :return: 
        """
        ancestry = []
        parent = self.rtParent
        while parent is not None:
            ancestry.append(parent.name)
            parent = parent.rtParent
        ancestry.reverse()
        return ancestry

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

