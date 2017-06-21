from program import Program
from settings import Settings
from lib.xmlhandler import loadLocalXMLFile, loadS3XMLFile
from os import path

# Do we have the program XML yet? If not, go get it.
program = Program()

class Project():

    def __init__(self, relPath):
        self.projname = "NO_NAME"
        self.projtype = "NO_TYPE"

        settings = Settings()
        self.localrootdir = settings.getSetting('DataDir')

        self.relPath = relPath
        self.pathArr = relPath.split("/")
        self.qItem = None
        self.rtItem = None
        self.remotePrefix = self.getRemoteS3Prefix()
        self.absProjectFile = self.getAbsProjFile()
        self.localprojroot = self.getAbsProjRoot()

        self.meta = []

    def load(self, remote=False):
        """
        We separate the load because it is intensive
        :param filepath:
        :param remote:
        :return:
        """
        if remote:
            self.DOM = loadS3XMLFile(program.Bucket, self.relPath)
        else:
            self.DOM = loadLocalXMLFile(self.absProjectFile)

        self.projname = self.DOM.find('Name').text.strip()
        self.projtype = self.DOM.find('ProjectType').text.strip()

        # Now print all the metadata values for reference
        metaNodes = self.DOM.findall('MetaData/Meta')
        for node in metaNodes:
            self.meta.append({
                "name": node.attrib['name'],
                "value": node.text.strip()
            })

    # Here are different forms the path can take

    def getAbsProjRoot(self):
        return path.dirname(path.join(self.localrootdir, path.sep.join(self.pathArr)))

    def getAbsProjFile(self):
        return path.join(self.localrootdir, path.sep.join(self.pathArr))

    def getRemoteS3Prefix(self):
        return path.dirname('/'.join(self.pathArr))

