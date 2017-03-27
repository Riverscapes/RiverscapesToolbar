# -*- coding: utf-8 -*-
"""
/***************************************************************************
This class is responsible for loading and maintining the GCD project file

"""

import os, re

from PyQt4.QtCore import *

from os import path
import xml.etree.ElementTree as ET
from toc_management import *
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
