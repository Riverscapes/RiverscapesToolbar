import xml.etree.ElementTree as ET
from s3.comparison import getS3getFileContents
from StringIO import StringIO

def loadLocalXMLFile(filepath):
    """
    Convenience method parse a filepath into a dom node and return the root
    :param file:
    :return:
    """
    with open(filepath, 'r') as myfile:
        data = myfile.read().replace('\n', '')
        it = ET.iterparse(StringIO(data))
        stripNamespaces(it)
        return it.root


def loadS3XMLFile(bucket, key):
    """
    Convenience method for parsing an XML file we pull from an S3 location
    :param bucket:
    :param key:
    :return:
    """
    xmlstr = getS3getFileContents(bucket, key)
    it = ET.fromstring(xmlstr)
    return it


def stripNamespaces(dom):

    # strip all namespaces. This is an XML antipattern but it makes the project SOOOOO much
    # easier to work with.
    for _, el in dom:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
