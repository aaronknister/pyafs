import errno
import os
from afs import _fs
from afs._fs import whichcell, lsmount

def inafs(path):
    """Return True if a path is in AFS."""
    try:
        whichcell(path)
    except OSError, e:
        if e.errno in (errno.EINVAL, errno.ENOENT):
            return False

    return True

def ismount(path):
    """Return True if a path is a mountpoint."""
    try:
        lsmount(path)
    except OSError, e:
        if e.errno in (errno.EINVAL, errno.ENOENT):
            return False
        raise

    return True

def mkmount(directory,volume,cell=None,rw=0):
    """Mount an AFS volume"""	
    cellularMount=0
    if cell:
        cellularMount=1
    
    if len(volume) > 64:
        raise Exception, 'volume name too long (length must be < 64 characters)'
    
    """ Check for a cell name in volume spec. and complain if it doesn't match
        what was specified with the cell option """
    if ':' in volume:
        tmpCell,tmpVolumeName=volume.split(':',1)
        if not tmpCell == cell:
            raise Exception, 'cell names do not match'
        else:
            volume=tmpVolume
            cell=tmpCell
    
    """ Make sure parent of directory is in afs """
    parentPath=os.path.dirname(os.path.normpath(directory))
    if not inafs(parentPath):
        raise Exception, 'parent directory is not in afs'

    """ If no cell has been defined thus far use the cell of the parent dir """
    if not cell:
        cell=whichcell(parentPath)
    
    """ Handle explicit rw volume mounts """
    mountTypeChar='#'
    if rw == 1:
        mountTypeChar='%' # if -rw specified
    
    """ For volume specs containing a cell name """
    cellularMountString=''
    if cellularMount:
        cellularMountString='%s:' % (cell)

    """ Create the mount by ways of a symbolic link """
    symlinkName='%s%s%s.' % (mountTypeChar,cellularMountString,volume)
    os.symlink(symlinkName,directory)
