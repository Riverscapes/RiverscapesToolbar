from lib.program import ProgramXML
from lib.s3.walkers import s3ProductWalker
from RiverscapesToolbar.settings import Settings
from PyQt4.QtGui import QStandardItem, QMenu, QStandardItemModel, QTreeView, QMessageBox, QIcon, QPixmap
from StringIO import StringIO
from os import path
from lib.toc_management import *

class DockWidgetTabRepository():

    def __init__(self, dockWidget):
        # used to be:
        # def __init__(self, xmlPath, treeControl, parent=None):
        # Connect up our buttons to functions
        dockWidget.btnRefresh.clicked.connect(self.btn_refresh)
        self.tree = self.treeRepository

    def btn_refresh(self):
        """
        Refresh the main dialog
        :return:
        """
        print "clicked"
        settings = Settings()
        program = ProgramXML(settings.getSetting('ProgramXMLUrl'))

        print 'Walking through and finding projects:'
        s3ProductWalker(program.Bucket)

        """ Constructor """
        if program is None:
            msg = "..."
            q = QMessageBox(QMessageBox.Warning, "Could not find that file", msg)
            q.setStandardButtons(QMessageBox.Ok)
            i = QIcon()
            i.addPixmap(QPixmap("..."), QIcon.Normal)
            q.setWindowIcon(i)
            q.exec_()
        else:
            self.model = QStandardItemModel()
            # Set up an invisible root item for the tree.
            # self.treeRoot = self.model.invisibleRootItem()
            self.treeRoot = QStandardItem("Root Item")
            self.model.appendRow(self.treeRoot)
            self.tree.setModel(self.model)
            self.tree.doubleClicked.connect(self.item_doubleClicked)
            self.tree.customContextMenuRequested.connect(self.openMenu)
            self.tree.setDragEnabled(True)

            self.xmlTreeDir = os.path.join(os.path.dirname(__file__), "Resources/XML/")
            self.namespace = "{http://tempuri.org/ProjectDS.xsd}"
            self.xmlTreePath = None

            # Set up the first domino for the recursion
            projectName = self.xmlProjectDoc.find("Project/name")
            if projectName is not None:
                self.treeRoot.setText(projectName.text)

            self.LoadNode(None, self.xmlTemplateDoc.find("node"), self.xmlProjectDoc)
            self.tree.expandToDepth(5)

    def LoadNode(self, tnParent, templateNode, projNode):
        """ Load a single node """
        data = {}
        label = self.getLabel(templateNode, projNode)

        # Detect if this is an XML node element and reset the root Project node to this.
        entityType = templateNode.find('entity/type')
        entityXPath = templateNode.find('entity/xpath')
        newProjNode = projNode

        if entityXPath is not None:
            newProjNode = projNode.find(entityXPath.text)

            # This node might be a leaf. If so we need to get some meta dat
        if entityType is not None and entityXPath is not None:
            filepathNode = projNode.find(entityXPath.text)
            if filepathNode is not None:
                # normalize the slashes
                # filepath = re.sub('[\\\/]+', os.path.sep, filepathNode.text)
                # make it an absolute path
                filepath = os.path.join(self.xmlProjDir, filepathNode.text)
                data['filepath'] = filepath
            if entityXPath is not None:
                data['xpath'] = entityXPath.text
            symbologyNode = templateNode.find('entity/symbology')
            if symbologyNode is not None:
                data['symbology'] = symbologyNode.text

        # Add the leaf to the tree
        newTreeItem = QStandardItem(label)

        if tnParent is None:
            self.treeRoot.appendRow(newTreeItem)
        else:
            tnParent = tnParent.appendRow(newTreeItem)

            # Just a regular node with children
        for xChild in templateNode.findall("children/node"):
            self.LoadNode(newTreeItem, xChild, newProjNode)
        for xRepeater in templateNode.findall("children/repeater"):
            self.LoadRepeater(newTreeItem, xRepeater, newProjNode)

        data['group_layers'] = self.getTreeAncestry(newTreeItem)
        newTreeItem.setData(data)

    def LoadRepeater(self, tnParent, templateNode, projNode):
        """ Repeater is for using an XPAth in the project file for repeating elements """

        label = self.getLabel(templateNode, projNode)

        newTreeItem = QStandardItem(label)
        if tnParent is None:
            self.treeRoot.appendRow(newTreeItem)
        else:
            tnParent = tnParent.appendRow(newTreeItem)

            # REmember, repeaters can only contain one "pattern" node
        xPatternNode = templateNode.find("node")

        # If there is an Xpath then reset the base project node to that.
        xpath = templateNode.find("xpath")
        xNewProjList = []
        if xPatternNode is not None and xpath is not None:
            absoluteXPath = xpath.text[:1] == "/"
            # Should we search from the root or not.
            if absoluteXPath:
                xNewProjList = self.xmlProjectDoc.findall("." + xpath.text)
            else:
                xNewProjList = projNode.findall(xpath.text)

        for xProjChild in xNewProjList:
            self.LoadNode(newTreeItem, xPatternNode, xProjChild)

    def getTreeAncestry(self, item):
        ancestry = []
        parent = item.parent()
        while parent is not None:
            ancestry.append(parent.text())
            parent = parent.parent()
        ancestry.reverse()
        return ancestry

    def item_doubleClicked(self, index):
        item = self.tree.selectedIndexes()[0]
        self.openProject(item.model().itemFromIndex(index))

    def openMenu(self, position):
        """ Handle the contextual menu """
        index = self.tree.selectedIndexes()[0]
        item = index.model().itemFromIndex(index)
        menu = QMenu()

        receiver = lambda item=item: self.openProject(item)
        menu.addAction("Open Project", receiver)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def getLabel(self, templateNode, projNode):
        """ Either use the liral text inside <label> or look it
            up in the project node if there's a <label xpath="/x/path">
        """
        labelNode = templateNode.find("label")
        label = "TITLE_NOT_FOUND"
        if labelNode is not None:
            if "xpath" in labelNode.attrib:
                xpath = labelNode.attrib['xpath']
                label = projNode.find(xpath).text
            else:
                label = labelNode.text

        return label

    def openProject(self, item):
        print "ADDING TO MAP::", item.data()
        itemExt = path.splitext(item.data()['filepath'])[1]
        if itemExt == '.shp':
            AddVectorLayer(item)
        else:
            AddRasterLayer(item)
