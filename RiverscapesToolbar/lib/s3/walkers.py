import os
import logging
from riverscapestools.userinput import querychoices

from transfers import Transfer
from operations import S3Operation

def s3BuildOps(conf):
    """
    Compare a source folder with what's already in S3 and given
    the direction you specify it should figure out what to do.

    conf = {
        "delete": args.delete,
        "force": args.force,
        "direction": direction,
        "localroot": path.join(datadir, keyprefix),
        "keyprefix": keyprefix,
        "bucket": program.Bucket
    }
    :return: opstore
    """
    s3 = Transfer(conf['bucket'])
    opstore = {}
    log = logging.getLogger()
    prefix = "{0}/".format(conf['keyprefix']).replace("//", "/")

    log.info('The following locations were found:')
    if conf['direction'] == S3Operation.Direction.UP:
        tostr = 's3://{0}/{1}'.format(conf['bucket'], conf['keyprefix'])
        fromstr = conf['localroot']
    else:
        fromstr = 's3://{0}/{1}'.format(conf['bucket'], conf['keyprefix'])
        tostr = conf['localroot']
    log.info('FROM: {0}'.format(fromstr))
    log.info('TO  : {0}'.format(tostr))


    log.info('The following operations are queued:')

    response = s3.list(prefix)

    # Get all the files we have locally
    files = {}
    if os.path.isdir(conf['localroot']):
        files = {}
        localProductWalker(conf['localroot'], files)

    # Fill in any files we find on the remote
    if 'Contents' in response:
        for result in response['Contents']:
            dstkey = result['Key'].replace(prefix, '')
            if dstkey in files:
                files[dstkey]['dst'] = result
            else:
                files[dstkey] = { 'dst': result }

    for relname in files:
        fileobj = files[relname]
        opstore[relname] = S3Operation(relname, fileobj, conf)

    if len(opstore) == 0:
        log.info("-- NO Operations Queued --")


    return opstore

def localProductWalker(projroot, filedict, currentdir=""):
    """
    This method has a similar recursive structure to s3FolderUpload
    but we're keeping it separate since it is only used to visualize
    the files in this folder
    :param rootDir:
    :param first:
    :return:
    """
    log = logging.getLogger()
    for pathseg in os.listdir(os.path.join(projroot, currentdir)):
        spaces = len(currentdir) * ' ' + '/'
        # Remember to sanitize for slash unity. We write unix separators
        # and then translate back to widnows when we need it.
        relpath = os.path.join(currentdir, pathseg).replace('\\', '/')
        abspath = os.path.join(projroot, relpath).replace('\\', '/')
        if os.path.isfile(abspath):
            log.debug(spaces + relpath)
            filedict[relpath] = { 'src': abspath }
        elif os.path.isdir(abspath):
            log.debug(spaces + pathseg + '/')
            localProductWalker(projroot, filedict, relpath)

def s3Exists(bucket, prefix):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return:
    """
    s3 = Transfer(bucket)
    result = False
    # list everything at this collection
    try:
        response = s3.list(prefix, Delimiter='/')
        if 'Contents' in response or 'CommonPrefixes' in response:
            print "Found:: " + prefix
            result = True
    except:
        pass
    return result


def s3HeadData(bucket, key):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return: A dictionary or None
    """
    s3 = Transfer(bucket)
    head = None
    # list everything at this collection
    try:
        response = s3.head(key, Delimiter='/')
        if 'Contents' in response or 'CommonPrefixes' in response:
            print "Found:: " + key
            result = True
    except:
        pass
    return head


def s3GetFolderList(bucket, prefix):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return:
    """
    log = logging.getLogger()
    s3 = Transfer(bucket)
    results = []
    # list everything at this collection
    response = s3.list(prefix, Delimiter='/')
    if 'CommonPrefixes' in response:
        for o in response.get('CommonPrefixes'):
            results.append(o['Prefix'].replace(prefix, '').replace('/', ''))
    return results

def s3ProductWalker(bucket, patharr, currpath=[], currlevel=0):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return:
    """
    log = logging.getLogger()
    s3 = Transfer(bucket)
    if currlevel >= len(patharr):
        return

    # If it's a collection then we need to iterate over folders and recurse on each
    if patharr[currlevel]['type'] == 'collection':
        # list everything at this collection
        pref = "/".join(currpath)+"/" if len(currpath) > 0 else ""
        result = s3.list(pref, Delimiter='/')
        if 'CommonPrefixes' in result:
            for o in result.get('CommonPrefixes'):
                s3ProductWalker(bucket, patharr, o.get('Prefix')[:-1].split('/'), currlevel + 1)
        else:
            return

    # If it's a container then no iteration necessary. Just append the path and recurse
    elif patharr[currlevel]['type'] == 'group':
        currpath.append(patharr[currlevel]['folder'])
        s3ProductWalker(bucket, patharr, currpath, currlevel + 1)

    # If it's a project then get the XML file and print it
    elif patharr[currlevel]['type'] == 'product':
        currpath.append(patharr[currlevel]['folder'])
        result = s3.list("/".join(currpath)+"/", Delimiter='/')
        if 'Contents' in result:
            for c in result['Contents']:
                if os.path.splitext(c['Key'])[1] == '.xml':
                    log.info('Project: {0} (Modified: {1})'.format(c['Key'], c['LastModified']))
        return

def menuwalk(program, nodes=None, currpath=[]):
    """
    Walks through the program letting users choose if it's a level
    or specify if it's a container It returns a set of program paths
    that we then need to go and lookup to make our download queue
    :param currlevelObj:
    :param path:
    :return:
    """
    log = logging.getLogger()
    if nodes is None:
        nodes = [program.Hierarchy]

    name = nodes[0]['node']['name'] if len(nodes) == 1 else ""

    # Get the list at the current path
    pathstr = '/'.join(currpath) + '/' if len(currpath) > 0 else ""
    levellist = s3GetFolderList(program.Bucket, pathstr)
    querystr = "Collection Choice: {0}{1}".format(pathstr, name)
    choicename = querychoices(querystr, levellist, "Select:")
    currpath.append(choicename)

    if len(nodes) > 1:
        node = getnodekeyval(nodes, 'folder', choicename)
    else:
        node = nodes[0]

    if node['type'] == 'product':
        pathstr = '/'.join(currpath) + '/' if len(currpath) > 0 else ""
        log.info("\nProduct Found: {0}".format(pathstr))
        return currpath

    # No we've made out choice. We need to move on.
    elif 'children' in node and len(node['children']) > 0:
        # child1 = node['children'][0]
        children = node['children']
        # if child1['type'] == 'collection':
        #     chil
        return menuwalk(program, children, currpath[:])


def getnodekeyval(thelist, key, val):
    return next(x for x in thelist if x['node'][key] == val)