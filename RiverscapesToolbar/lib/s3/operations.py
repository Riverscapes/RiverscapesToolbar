import os
import logging
from comparison import s3issame
from transfers import FileTransfer
from PyQt4.QtCore import QThread, pyqtSignal, QObject, pyqtSlot

class S3Operation:
    """
    A Simple class for storing src/dst file information and the operation we need to perform
    """
    class FileOps:
        # Kind of an enumeration
        DELETE_REMOTE = "Delete Remote"
        DELETE_LOCAL = "Delete Local"
        UPLOAD = "Upload"
        DOWNLOAD = "Download"
        IGNORE = "Ignore"

    class Direction:
        # Kind of an enumeration
        UP = "up"
        DOWN = "down"

    class FileState:
        # Kind of an enumeration
        LOCALONLY = "Local-Only"
        REMOTEONLY = "Remote-Only"
        UPDATENEEDED = "Update Needed"
        SAME = "Files Match"

    progressSignal = pyqtSignal(object)

    def __init__(self, key, fileobj, conf):
        """
        :param key: The relative key/path of the file in question
        :param fileobj: the file object with 'src' and 'dst'
        :param conf: the configuration dictionary
        """


        self.log = logging.getLogger()
        self.log.setLevel(logging.ERROR)
        self.s3 = FileTransfer(conf.bucket, self.updateProgress)
        self.key = key
        self.progress = 0

        # Set some sensible defaults
        self.filestate = self.FileState.SAME
        self.op = self.FileOps.IGNORE

        self.delete = conf.delete
        self.force = conf.force
        self.localroot = conf.localroot
        self.bucket = conf.bucket
        self.direction = conf.direction
        self.keyprefix = conf.keyprefix
        self.s3size = 0

        # And the final paths we use:
        self.abspath = self.getAbsLocalPath()
        self.fullkey = self.getS3Key()

        # The remote size (if it exists) helps us figure out percent done
        if 'dst' in fileobj:
            self.s3size = fileobj['dst']['Size']

        # Figure out what we have
        if 'src' in fileobj and 'dst' not in fileobj:
            self.filestate = self.FileState.LOCALONLY

        if 'src' not in fileobj and 'dst' in fileobj:
            self.filestate = self.FileState.REMOTEONLY

        if 'src' in fileobj and 'dst' in fileobj:
            if s3issame(fileobj['src'], fileobj['dst']):
                self.filestate = self.FileState.SAME
            else:
                self.filestate = self.FileState.UPDATENEEDED

        # The Upload Case
        # ------------------------------
        if self.direction == self.Direction.UP:
            # Two cases for uploading the file: New file or different file
            if self.filestate == self.FileState.LOCALONLY or self.filestate == self.FileState.UPDATENEEDED:
                self.op = self.FileOps.UPLOAD

            # If we've requested a force, do the upload anyway
            elif self.FileState.SAME and self.force:
                self.op = self.FileOps.UPLOAD

            # If the remote is there but the local is not and we're uploading then clean up the remote
            # this requires thed delete flag be set
            elif self.filestate == self.FileState.REMOTEONLY and self.delete:
                self.op = self.FileOps.DELETE_REMOTE

        # The Download Case
        # ------------------------------
        elif self.direction == self.Direction.DOWN:
            if self.filestate == self.FileState.REMOTEONLY or self.filestate == self.FileState.UPDATENEEDED:
                self.op = self.FileOps.DOWNLOAD

            # If we've requested a force, do the download anyway
            elif self.FileState.SAME and self.force:
                self.op = self.FileOps.DOWNLOAD

            # If the local is there but the remote is not and we're downloading then clean up the local
            # this requires thed delete flag be set
            elif self.filestate == self.FileState.LOCALONLY and self.delete:
                self.op = self.FileOps.DELETE_LOCAL

        self.log.info(str(self))

    def getS3Key(self):
        # Not using path.join because can't be guaranteed a unix system
        return "{1}/{2}".format(self.bucket, self.keyprefix, self.key)

    def getAbsLocalPath(self):
        # Not using path.join because can't be guaranteed a unix system
        return os.path.join(self.localroot, self.key)

    def execute(self):
        """
        Actually run the command to upload/download/delete the file
        :return:
        """
        self.progress = 0
        if self.op == self.FileOps.IGNORE:
            self.log.info(" [{0}] {1}: Nothing to do. Continuing.".format(self.op, self.key))

        elif self.op == self.FileOps.UPLOAD:
            self.upload()

        elif self.op == self.FileOps.DOWNLOAD:
            self.download()

        elif self.op == self.FileOps.DELETE_LOCAL:
            self.delete_local()

        elif self.op == self.FileOps.DELETE_REMOTE:
            self.delete_remote()

        self.progress = 100

    def __repr__(self):
        """
        When we print this class as a string this is what we output
        """
        forcestr = "(FORCE)" if self.force else ""
        opstr = "{0:12s} ={2}=> {1:10s}".format(self.filestate, self.op, forcestr)
        return "./{1:60s} [ {0:21s} ]".format(opstr.strip(), self.key)


    def updateProgress(self, prog):
        self.progress = prog


    def delete_remote(self):
        """
        Delete a Remote file
        """
        self.log.info("Deleting: {0} ==> ".format(self.fullkey))
        # This step prints straight to stdout and does not log
        self.s3.delete(self.fullkey)
        self.log.debug("S3 Deletion Completed: {0}".format(self.fullkey))

    def delete_local(self):
        """
        Delete a local file
        """
        dirname = os.path.dirname(self.abspath)
        os.remove(self.abspath)
        self.log.info("Deleting Local file: {0} ==> ".format(self.abspath))
        # now walk backwards and clean up empty folders
        try:
            os.removedirs(dirname)
            self.log.debug('Cleaning up folders: {0}'.format(dirname))
        except:
            self.log.debug('Folder cleanup stopped since there were still files: {0}'.format(dirname))
            pass
        self.log.debug("Local Deletion Completed: {0}".format(self.abspath))


    def download(self):
        """
        Just upload one file using Boto3
        :param bucket:
        :param key:
        :param filepath:
        :return:
        """

        # Make a directory if that's needed
        dirpath = os.path.dirname(self.abspath)
        if not os.path.exists(dirpath):
            try:
                os.makedirs(dirpath)
            except Exception as e:
                raise Exception("ERROR: Directory `{0}` could not be created.".format(dirpath))

        self.log.info("Downloading: {0} ==> ".format(self.fullkey))
        # This step prints straight to stdout and does not log
        self.s3.download(self.fullkey, self.abspath, size=self.s3size)
        print ""
        self.log.debug("Download Completed: {0}".format(self.abspath))

    def upload(self):
        """
        Just upload one file using Boto3
        :param bucket:
        :param key:
        :param filepath:
        :return:
        """

        self.log.info("Uploading: {0} ==> s3://{1}/{2}".format(self.abspath, self.bucket, self.fullkey))
        # This step prints straight to stdout and does not log
        self.s3.upload(self.abspath, self.fullkey)
        print ""
        self.log.debug("Upload Completed: {0}".format(self.abspath))



