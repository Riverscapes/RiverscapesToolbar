from program import Program
from settings import Settings
from lib.xmlhandler import loadLocalXMLFile, loadS3XMLFile
from os import path

# Do we have the program XML yet? If not, go get it.
program = Program()

class Project():

    def __init__(self, projPath, outside=False):
        """
        Outside means the file is living in a folder that is not in the current structure.
        :param projPath: relative path unless outside is set True
        :param outside:
        """
        self.projname = "NO_NAME"
        self.projtype = "NO_TYPE"

        # This is the raw projPath. It can be relative or absolute so don't use it outside this class
        self._projpath = projPath

        settings = Settings()
        self.outside = outside
        self.qItem = None
        self.meta = []
        self.relPath = None
        self.localrootdir = settings.getSetting('DataDir')
        self.DOM = None

        self.relPath = projPath
        self.pathArr = self.relPath.split("/")

        # SPECIAL CASE: This file may come from some weird folder outside the repo
        if outside:
            self.absProjectFile = projPath
            self.load(remote=False)

            # Now we have the metadata we can invent the rest of the path
            # Now we
            self.relPath = self.getPath()
            self.pathArr = self.relPath.split("/")

            if path.normpath(path.join(self.localrootdir, self.relPath)) == path.normpath(projPath):
                outside = False

        else:
            self.absProjectFile = self.getAbsProjFile()


        self.remotePrefix = self.getRemoteS3Prefix()
        self.localprojroot = self.getAbsProjRoot()


    def load(self, remote=False):
        """
        We separate the load because it is intensive
        :param filepath:
        :param remote:
        :return:
        """
        if self.DOM is None:
            if remote and program.valid:
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

    def getPath(self):
        """
        Figure out what the repository path should be
        :param project:
        :param program:
        :return:
        """

        def _strnullorempty(str):
            return str is None or len(str.strip()) == 0

        # First let's get the project type
        projType = self.DOM.find('./ProjectType').text.strip()
        assert not _strnullorempty(projType), "ERROR: <ProjectType> not found in project XML."
        print "Project Type Detected: {0}".format(projType)

        # Now go get the product node from the program XML
        patharr = program.findprojpath(projType)
        assert program.valid is not None, "ERROR: Program must be loaded for this to work"
        assert patharr is not None,  "ERROR: Product '{0}' not found anywhere in the program XML".format(projType)

        extpath = ''
        for idx, level in enumerate(patharr):
            if level['type'] == 'collection':
                col = self.getcollection(level['name'])
                print "{0}/collection:{1} => {2}".format(idx*'  ', level['name'], col)
                name = col
                if program.testAllowedCollection(level['id'], col):
                    name = program.getAllowedLookup(level['id'], col)
                extpath += '/' + name
            elif level['type'] == 'group':
                print "{0}/group:{1}".format(idx * '  ', level['name'])
                extpath += '/' + level['folder']
            elif level['type'] == 'product':
                print "{0}/product:{1}".format(idx * '  ', level['name'])
                extpath += '/' + level['folder']

        # Trim the first slash for consistency elsewhere
        if len(extpath) > 0 and extpath[0] == '/':
            extpath = extpath[1:]

        print "Final remote path to product: {0}".format(extpath)

        return "/".join([extpath, program.ProjectFile])

    def getcollection(self, colname):
        """
        Try to pull the Collection out of the project file
        :param colname: string with the Collection we're looking for
        :param project: the ET node with the project xml
        :return:
        """
        try:
            val = self.DOM.find("MetaData/Meta[@name='{0}']".format(colname)).text.strip()
        except AttributeError:
            raise ValueError("ERROR: Could not find <Meta name='{0}'>########</Meta> tag in project XML".format(colname))
        return val

    def getAbsProjRoot(self):
        if self.outside:
            return path.dirname(self._projpath)
        else:
            return path.dirname(path.join(self.localrootdir, path.sep.join(self.pathArr)))

    def getAbsProjFile(self):
        if self.outside:
            return self._projpath
        else:
            return path.join(self.localrootdir, path.sep.join(self.pathArr))

    def getRemoteS3Prefix(self):
        return path.dirname('/'.join(self.pathArr))

