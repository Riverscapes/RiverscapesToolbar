import threading
import os
import sys
import math
import boto3
from boto3.s3.transfer import TransferConfig
from PyQt4.QtCore import pyqtSignal, QObject, pyqtSlot

class AWSCredsBorg(object):
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state

class AWSCreds(AWSCredsBorg):
    """
    Read up on the Borg pattern if you don't already know it. Super useful
    """
    def __init__(self, creds=None):
        super(AWSCreds, self).__init__()
        if creds is not None:
            self.creds = creds

class FileTransfer(QObject):
    # Max size in bytes before uploading in parts.
    # Specifying this is important as it affects
    # How the MD5 and Etag is calculated
    AWS_UPLOAD_MAX_SIZE = 20 * 1024 * 1024
    # Size of parts when uploading in parts
    AWS_UPLOAD_PART_SIZE = 6 * 1024 * 1024

    progsignal = pyqtSignal(tuple)

    def __init__(self, bucket):

        super(FileTransfer, self).__init__()
        # Get the service client
        creds = AWSCreds()
        self.s3 = boto3.client('s3', **creds.creds)
        self.bucket = bucket
        self.filepath = None
        self.filesize = 0
        self.percentdone = 0
        self.S3Config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=self.AWS_UPLOAD_MAX_SIZE,
            max_concurrency=10,
            num_download_attempts=10,
            multipart_chunksize=self.AWS_UPLOAD_PART_SIZE,
            max_io_queue=10000
        )

    def download(self, key, filepath, **kwargs):
        self.filepath = filepath
        if 'size' in kwargs:
            self.filesize = kwargs['size']
        else:
            self.filesize = self.getDiskSize(filepath)
        self.s3.download_file(self.bucket, key, filepath, Config=self.S3Config, Callback=Progress(self.progCallback))

    def upload(self, filepath, key):
        self.filepath = filepath
        self.filesize = self.getDiskSize(filepath)
        self.s3.upload_file(filepath, self.bucket, key, Config=self.S3Config, Callback=Progress(self.progCallback))


    def delete(self, key):
        self.s3.delete_object(Bucket=self.bucket, Key=key)

    def list(self, prefix, **kwargs):
        return self.s3.list_objects(Bucket=self.bucket, Prefix=prefix, **kwargs)

    def head(self, key, **kwargs):
        return self.s3.head_object(Bucket=self.bucket, Key=key, **kwargs)

    def progCallback(self, bytessofar):
        if self.filesize > 0:
            self.percentdone = math.floor(float(bytessofar) / float(self.filesize) * 100)

        # print "Progress: {} -- {}".format(self.percentdone, self.filepath)
        self.progsignal.emit((self.filepath, self.percentdone, bytessofar, self.filesize))

    @staticmethod
    def getDiskSize(filepath):
        if os.path.isfile(filepath):
            return os.stat(filepath).st_size
        else:
            return 0

class Progress():
    """
    A Little helper class to display the up/download percentage
    """

    def __init__(self, progcb):
        self._seen_so_far = 0
        self.progcb = progcb
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            self.progcb(self._seen_so_far)

