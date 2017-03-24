import botocore
import binascii
import hashlib
import os
from transfers import Transfer

def s3issame(filepath, s3obj):
    """
    Check to see if our local file has the same md5/etag
    as what's in S3
    :param bucket: S3 bucket name
    :param key: S3 key (minus the s3://bucketname)
    :param filepath: Absolute local filepath
    :return: Boolean
    """
    etag = None
    same = False
    try:
        etag = s3obj['ETag'][1:-1]
    except botocore.exceptions.ClientError as e:
        pass

    if etag is None:
        same = False
    else:
        # check MD5
        md5 = md5sum(filepath)
        same = True if etag == md5 else False
    return same


def md5sum(sourcePath):
    """
    Get the md5 hash of a file stored in S3

        Source: https://github.com/hhagblom/lambda-decorators/blob/master/awslambdadecorators/s3etag.py

    :param sourcePath: local filepath
    :return: Returns the md5 hash that will match the ETag in S3
    """
    filesize = os.path.getsize(sourcePath)
    hash = hashlib.md5()

    if filesize > Transfer.AWS_UPLOAD_MAX_SIZE:

        block_count = 0
        md5string = ""
        with open(sourcePath, "r+b") as f:
            for block in iter(lambda: f.read(Transfer.AWS_UPLOAD_PART_SIZE), ""):
                hash = hashlib.md5()
                hash.update(block)
                md5string = md5string + binascii.unhexlify(hash.hexdigest())
                block_count += 1

        hash = hashlib.md5()
        hash.update(md5string)
        return hash.hexdigest() + "-" + str(block_count)

    else:
        with open(sourcePath, "r+b") as f:
            for block in iter(lambda: f.read(Transfer.AWS_UPLOAD_PART_SIZE), ""):
                hash.update(block)
        return hash.hexdigest()