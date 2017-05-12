import threading
import os
import sys
import math
import boto3
from boto3.s3.transfer import TransferConfig

class FileTransfer:
    # Max size in bytes before uploading in parts.
    # Specifying this is important as it affects
    # How the MD5 and Etag is calculated
    AWS_UPLOAD_MAX_SIZE = 20 * 1024 * 1024
    # Size of parts when uploading in parts
    AWS_UPLOAD_PART_SIZE = 6 * 1024 * 1024

    def __init__(self, bucket, progCallback=None):

        # Get the service client
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.progCallback = progCallback
        self.S3Config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=self.AWS_UPLOAD_MAX_SIZE,
            max_concurrency=10,
            num_download_attempts=10,
            multipart_chunksize=self.AWS_UPLOAD_PART_SIZE,
            max_io_queue=10000
        )

    def download(self, key, filepath, **kwargs):
        self.s3.download_file(self.bucket, key, filepath, Config=self.S3Config, Callback=Progress(filepath, self.progCallback, **kwargs))

    def upload(self, filepath, key):
        self.s3.upload_file(filepath, self.bucket, key, Config=self.S3Config, Callback=Progress(filepath, self.progCallback))

    def delete(self, key):
        self.s3.delete_object(Bucket=self.bucket, Key=key)

    def list(self, prefix, **kwargs):
        return self.s3.list_objects(Bucket=self.bucket, Prefix=prefix, **kwargs)

    def head(self, key, **kwargs):
        return self.s3.head_object(Bucket=self.bucket, Key=key, **kwargs)

class Progress(object):
    """
    A Little helper class to display the up/download percentage
    """
    def __init__(self, filename, progCallback, **kwargs):
        self._filename = filename
        self._progCallback = progCallback
        self._basename = os.path.basename(self._filename)

        if 'size' in kwargs:
            self._filesize = kwargs['size']
        else:
            self._filesize = self.getSize()

        self._seen_so_far = 0
        self._lock = threading.Lock()

    def getSize(self):
        if os.path.isfile(self._filename):
            return os.stat(self._filename).st_size
        else:
            return 0

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            self.percentdone = 0
            if self._filesize > 0:
                self.percentdone = math.floor(float(self._seen_so_far) / float(self._filesize) * 100)
            else:
                self.getSize()
            self._progCallback(self.percentdone)
