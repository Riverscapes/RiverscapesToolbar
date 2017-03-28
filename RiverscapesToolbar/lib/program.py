import urllib2
import re
import logging
import xml.etree.ElementTree as ET

class ProgramXML():
    def __init__(self, xmpProgUrl):

        self.DOM = None
        self.getProgram(xmpProgUrl)
        self.Collections = {}
        self.Groups = {}
        self.Products = {}
        self.Hierarchy = {}
        self.Bucket = None
        self.log = logging.getLogger()

        # Populate everything
        self.getBucket()
        self.getProjectFile()
        self.parseCollections()
        self.parseGroups()
        self.parseProducts()
        self.parseTree(self.DOM.find('Hierarchy/*'))

    def parseCollections(self):
        """
        Pull all the collections out of the program XML
        :return:
        """
        for col in self.DOM.findall('Definitions/Collections/Collection'):
            self.Collections[col.attrib['id']] = {
                'id': col.attrib['id'],
                'type': 'collection',
                'name': col.attrib['name'],
                'allows': self.parseCollectionAllowed(col.findall('Allow'))
            }
            allowType = 'fixed'
            allows = self.Collections[col.attrib['id']]['allows']
            if len(allows) > 0:
                allowType = allows[0]['type']
            self.Collections[col.attrib['id']]['allowtype'] = allowType

    def getProgram(self, progpath):
        """
        Either uses a local path or downloads an online version of the program XML
        :param path:
        :return:
        """
        if re.match('^https*:\/\/.*', progpath) is not None:
            try:
                request = urllib2.Request(progpath)
                request.add_header('Pragma', 'no-cache')
                file = urllib2.build_opener().open(request)
                data = file.read()
                file.close()
                self.DOM = ET.fromstring(data)
            except:
                err = "ERROR: Could not download <{0}>".format(progpath)
                self.log.error(err)
                raise ValueError(err)
        else:
            self.DOM = ET.parse(progpath).getroot()

    def parseCollectionAllowed(self, allowETs):
        allows = []
        for allow in allowETs:
            if 'pattern' in allow.attrib:
                allows.append({
                    'type': 'pattern',
                    'pattern': allow.attrib['pattern'],
                })
            else:
                allows.append({
                    'type': 'fixed',
                    'name': allow.attrib['name'],
                    'folder': allow.attrib['folder']
                })
        return allows

    def testAllowedCollection(self, colName, desiredName):
        """
        Test if this is a valid collection to ask for
        :param collection:
        :param colName:
        :return:
        """
        collection = self.Collections[colName]
        if len(collection['allows']) == 0:
            return True

        assert len(desiredName) > 0, "ERROR: Desired collection name for collection {0} is empty.".format(collection['name'])

        bGood = False
        for allow in collection['allows']:
            if allow['type'] == 'pattern':
                try:
                    matchObj = re.match(allow['pattern'], desiredName)
                    if matchObj:
                        bGood = True
                        continue
                except Exception as e:
                    self.log.error("Something went wrong with the allow RegEx in the Program XML file", e)
                    raise e
            else:
                if allow['name'] == desiredName:
                    bGood = True
                    continue

        assert bGood, "ERROR: Desired Collection: {0} did not pass the allowed values test for collection: {1}".format(desiredName, collection['name'])
        return bGood

    def getAllowedLookup(self, colName, desiredName):
        """
        Get the actual allowed name. Most of the time this is just what you pass in
        but in the case of non-pattern allows this will do a lookup
        :param collection:
        :param colName:
        :return:
        """
        if len(self.Collections[colName]['allows']) == 0:
            return desiredName

        name = desiredName
        for allow in self.Collections[colName]['allows']:
            if allow['type'] == 'fixed' and allow['name'] == desiredName:
                name = allow['folder']
                continue
        return name

    def parseGroups(self):
        for grp in self.DOM.findall('Definitions/Groups/Group'):
            self.Groups[grp.attrib['id']] = {
                'id': grp.attrib['id'],
                'type': 'group',
                'name': grp.attrib['name'],
                'folder': grp.attrib['folder']
            }

    def parseProducts(self):
        for prod in self.DOM.findall('Definitions/Products/Product'):
            self.Products[prod.attrib['id']] = {
                'id': prod.attrib['id'],
                'type': 'product',
                'name': prod.attrib['name'],
                'folder': prod.attrib['folder']
            }

    def parseTree(self, etNode, treeNode = None):

        obj = {}

        if etNode.tag == 'Product' and 'ref' in etNode.attrib:
            obj['type'] = 'product'
            obj['node'] = self.Products[etNode.attrib['ref']]

        elif etNode.tag in ['Group', 'Collection']:
            obj['children'] = []
            if etNode.tag == 'Group':
                obj['type'] = 'group'
                obj['node'] = self.Groups[etNode.attrib['ref']]
            else:
                obj['type'] = 'collection'
                obj['node'] = self.Collections[etNode.attrib['ref']]

            for child in list(etNode):
                obj['children'].append(self.parseTree(child, obj['children']) )

        if treeNode is None:
            self.Hierarchy = obj

        return obj

    def getProjectFile(self):
        try:
            self.ProjectFile = self.DOM.find("MetaData/Meta[@name='projectfile']").text.strip()
            self.log.info("Project File we're looking for: {0}".format(self.ProjectFile))
        except:
            msg = "ERROR: No <Meta Name='projectfile'>project.rs.xml</Meta> tag found in program XML"
            self.log.error(msg)
            raise ValueError(msg)

    def getBucket(self):
        try:
            self.Bucket = self.DOM.find("MetaData/Meta[@name='s3bucket']").text.strip()
            self.log.info("S3 Bucket Detected: {0}".format(self.Bucket))
        except:
            msg = "ERROR: No <Meta Name='s3bucket'>riverscapes</Meta> tag found in program XML"
            self.log.error(msg)
            raise ValueError(msg)

    def getProdPath(self, prodName):

        self.log.title('Getting remote path structure...')

        # First let's get the project type
        assert not _strnullorempty(prodName), "ERROR: <ProjectType> not found in project XML."
        self.log.info("Project Type Detected: {0}".format(prodName))

        # Now go get the product node from the program XML
        patharr = self.findprojpath(prodName)
        assert patharr is not None, "ERROR: Product '{0}' not found anywhere in the program XML".format(prodName)
        self.log.title("Building Path to Product: ".format(prodName))

        return patharr

    def findprojpath(self, prodname, node=None, path=[]):
        """
        Find the path to the desired project
        :param prodname:
        :param node:
        :param path:
        :return:
        """
        if node is None:
            node = self.Hierarchy
        if node['type'] == 'product' and node['node']['name'] == prodname:
            path.append(node['node'])
            return path
        elif node['type'] in ['group', 'collection']:

            newpath = path[:]
            newpath.append(node['node'])

            for child in node['children']:
                result = self.findprojpath(prodname, child, newpath)
                if result is not None:
                    return result

    def progtos3path(self, progpath, level=0, currpath=[], paths=[]):
        """
        A program path to a series of real S3 paths
        :param progpath:
        :param level:
        :param currpath:
        :param paths:
        :return:
        """
        # Are we at the end yet? last level must be a product
        if (level - 1) == len(progpath):
            currpath.append(progpath[level])
            paths.append('/'.join(currpath))
            return paths

        # One choice. Just move on:
        if len(progpath[level]) == 1:
            currpath.append(progpath[level])
            self.progtos3path(progpath, level+1, paths)
        else:
            for el in progpath[level]:
                newpath = currpath[:].append(el)
                self.progtos3path(progpath, level+1, paths)

def _strnullorempty(str):
    return str is None or len(str.strip()) == 0

def getkeyval(thelist, key, val):
    return next(x for x in thelist if x[key] == val)
