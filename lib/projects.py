# -*- coding: utf-8 -*-
"""
/***************************************************************************
This class is responsible for loading and maintining the GCD project file

"""

import os, re
from PyQt4 import QtGui
from PyQt4.QtGui import QStandardItem, QMenu, QStandardItemModel, QTreeView, QMessageBox, QIcon, QPixmap
from PyQt4.QtCore import *
from StringIO import StringIO
from os import path
import xml.etree.ElementTree as ET

from toc_management import *

from riverscapestools import Logger
import xml.etree.ElementTree as ET
from os import path

# class Project():
#
#     def __init__(self, projectRoot, projXMLFile):
#         self.log = Logger('Project')
#         self.DOM = None
#         self.getProgramFromXML(path.join(projectRoot, projXMLFile))
#         self.LocalRoot = projectRoot
#
#     def getProgramFromXML(self, progXMLpath):
#         assert path.isfile(progXMLpath), "ERROR: could not find file called: {}".format(progXMLpath)
#         self.DOM = ET.parse(progXMLpath).getroot()
#
#     def getPath(self, program):
#         """
#         Figure out what the repository path should be
#         :param project:
#         :param program:
#         :return:
#         """
#         self.log.title('Getting remote path...')
#
#         # First let's get the project type
#         projType = self.DOM.find('./ProjectType').text.strip()
#         assert not _strnullorempty(projType), "ERROR: <ProjectType> not found in project XML."
#         self.log.info("Project Type Detected: {0}".format(projType))
#
#         # Now go get the product node from the program XML
#         patharr = program.findprojpath(projType)
#         assert patharr is not None,  "ERROR: Product '{0}' not found anywhere in the program XML".format(projType)
#         self.log.title("Building Path to Product: ".format(projType))
#
#         extpath = ''
#         for idx, level in enumerate(patharr):
#             if level['type'] == 'collection':
#                 col = self.getcollection(level['name'])
#                 self.log.info("{0}/collection:{1} => {2}".format(idx*'  ', level['name'], col))
#                 name = col
#                 if program.testAllowedCollection(level['id'], col):
#                     name = program.getAllowedLookup(level['id'], col)
#                 extpath += '/' + name
#             elif level['type'] == 'group':
#                 self.log.info("{0}/group:{1}".format(idx * '  ', level['name']))
#                 extpath += '/' + level['folder']
#             elif level['type'] == 'product':
#                 self.log.info("{0}/product:{1}".format(idx * '  ', level['name']))
#                 extpath += '/' + level['folder']
#
#         # Trim the first slash for consistency elsewhere
#         if len(extpath) > 0 and extpath[0] == '/':
#             extpath = extpath[1:]
#         self.log.info("Final remote path to product: {0}".format(extpath))
#
#         return extpath
#
#     def getcollection(self, colname):
#         """
#         Try to pull the Collection out of the project file
#         :param colname: string with the Collection we're looking for
#         :param project: the ET node with the project xml
#         :return:
#         """
#         try:
#             val = self.DOM.find("MetaData/Meta[@name='{0}']".format(colname)).text.strip()
#         except AttributeError:
#             raise ValueError("ERROR: Could not find <Meta name='{0}'>########</Meta> tag in project XML".format(colname))
#         return val
#
# def _strnullorempty(str):
#     return str is None or len(str.strip()) == 0

class ProjectXML():
    
    def __init__(self, xmlPath, treeControl, parent = None):
        """ Constructor """
        if xmlPath is None or not os.path.isfile(xmlPath):
            msg = "..."
            q = QMessageBox(QMessageBox.Warning, "Could not find that file",  msg)
            q.setStandardButtons(QMessageBox.Ok)
            i = QIcon()
            i.addPixmap(QPixmap("..."), QIcon.Normal)
            q.setWindowIcon(i)
            q.exec_()
        else:
            self.tree = treeControl
            self.model = QStandardItemModel()
            # Set up an invisible root item for the tree.
            #self.treeRoot = self.model.invisibleRootItem()
            self.treeRoot = QStandardItem("Root Item")
            self.model.appendRow(self.treeRoot)
            self.tree.setModel(self.model)
            self.tree.doubleClicked.connect(self.item_doubleClicked)
            self.tree.customContextMenuRequested.connect(self.openMenu)
            self.tree.setDragEnabled(True)

            self.xmlTreeDir = os.path.join(os.path.dirname(__file__), "Resources/XML/")
            self.xmlProjfile = xmlPath
            self.xmlProjDir = os.path.dirname(xmlPath)
            self.namespace = "{http://tempuri.org/ProjectDS.xsd}"
            self.xmlTreePath = None

            # Load the GCD Project (the raw data that will be used to populate the tree)
            # instead of ET.fromstring(xml)
            self.xmlProjectDoc = self.LoadXMLFile(self.xmlProjfile)

            if self.FindTreeParser():
                print "got ya"
                # Load the tree file (the rules we use to build the tree)

            else:
                print "This is an error"


            # Set up the first domino for the recursion         
            projectName = self.xmlProjectDoc.find("Project/name")
            if projectName is not None:
                self.treeRoot.setText(projectName.text)
   
            self.LoadNode(None, self.xmlTemplateDoc.find("node"), self.xmlProjectDoc)
            self.tree.expandToDepth(5)
          
    def FindTreeParser(self):
        # Now we need to figure out which kind of project it is.
        for subdir, dirs, files in os.walk(self.xmlTreeDir):
            for filename in files:
                if filename.endswith(".xml"):
                    filePath = os.path.join(subdir, filename)
                    candidate = self.LoadXMLFile( filePath )
                    testNode = candidate.find('test')
                    if len(testNode.text) > 10 and not testNode is None:
                        if self.xmlProjectDoc.find("./" +testNode.text) is not None:
                            found = True
                            self.xmlTreePath = filePath
                            self.xmlTemplateDoc = ET.parse(self.xmlTreePath)
                            return True
        return False
             
    def LoadXMLFile(self, file):
        with open(file, 'r') as myfile:
            data=myfile.read().replace('\n', '')
            it = ET.iterparse(StringIO(data))
            # strip all namespaces
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1] 
            return it.root

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
        self.addToMap( item.model().itemFromIndex(index))
    
    

    def openMenu(self, position):
        """ Handle the contextual menu """
        index = self.tree.selectedIndexes()[0]
        item = index.model().itemFromIndex(index)
        menu = QMenu()
        
        receiver = lambda item=item: self.addToMap(item)
        menu.addAction("Add to Map", receiver)

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
    
    def addToMap(self, item):
        print "ADDING TO MAP::", item.data()
        itemExt = path.splitext(item.data()['filepath'])[1]
        if itemExt == '.shp':
            AddVectorLayer(item)
        else:
            AddRasterLayer(item)
        