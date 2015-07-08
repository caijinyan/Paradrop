###################################################################
# Copyright 2013-2014 All Rights Reserved
# Authors: The Paradrop Team
###################################################################

import os, subprocess, shutil, traceback
from distutils import dir_util

# We have to import this for the decorator
from paradrop.internal.utils import unittest

#protect the original open function
__open = open

# Since we overwrite everything else, do the same to basename
basename = lambda x: os.path.basename(x)

@unittest.fixmount
def getMountCmd():
    return "mount"

def isMount(mnt):
    """This function checks if @mnt is actually mounted."""
    # TODO - need to check if partition and mount match the expected??
    return os.path.ismount(mnt)
        
def doMount(part, mnt):
    """This function mounts @part to @mnt."""
    # Since we are already in a deferred chain, use subprocess to block and make the call to mount right HERE AND NOW
    proc = subprocess.Popen("%s %s %s" % (getMountCmd(), part, mnt), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = proc.communicate()

    if(proc.returncode):
        out.err("!! %s Unable to mount (%d) %s\n" % (logPrefix(), proc.returncode, errors))
        raise Exception('UnableToMount', 'Mount error for %s' % mnt)

def doUnmount(mnt):
    """This function unmounts @mnt."""
    # Since we are already in a deferred chain, use subprocess to block and make the call to mount right HERE AND NOW
    proc = subprocess.Popen("umount %s" % (mnt), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = proc.communicate()

    if(proc.returncode):
        out.err("!! %s Unable to mount (%d) %s\n" % (logPrefix(), proc.returncode, errors))
        raise Exception('UnableToUnmount', 'Mount error for %s' % mnt)

def oscall(cmd, get=False):
    """
        This function performs a OS subprocess call.
        All output is thrown away unless an error has occured or if @get is True
        Arguments:
            @cmd: the string command to run
            [get] : True means return (stdout, stderr)
        Returns:
            None if not @get and no error
            (stdout, retcode, stderr) if @get or yes error
    """
    # Since we are already in a deferred chain, use subprocess to block and make the call to mount right HERE AND NOW
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = proc.communicate()
    if(proc.returncode or get):
        return (output, proc.returncode, errors)
    else:
        if(output and output != ""):
            out.verbose('-- %s "%s" stdout: "%s"\n' % (logPrefix(), cmd, output.rstrip()))
        if(errors and errors != ""):
            out.verbose('-- %s "%s" stderr: "%s"\n' % (logPrefix(), cmd, errors.rstrip()))
        return None

def syncFS():
    oscall('sync')

def getFileType(f):
    r = oscall('file "%s"' % f, True)
    if(r is not None and isinstance(r, tuple)):
        return r[0]
    else:
        return None

@unittest.fixpath
def exists(p):
    return os.path.exists(p)

@unittest.fixpath
def unlink(p):
    return os.unlink(p)

@unittest.fixpath
def mkdir(p):
    return os.mkdir(p)

@unittest.fixpath
def symlink(a, b):
    return os.symlink(a, b)

def makedirs(p):
    """Like the real make dirs function, except we cannot use it on Mac OS X machines."""
    # Make sure we have the abs path
    ap = os.path.abspath(p)
    buildUp = "/"
    for d in p.split('/'):
        if(not d):
            continue
        # Build up the path from root using the buildUp var
        buildUp += d + '/'
        # Check if it exists, if not make it
        # make sure to use our exists function in case its a unittest
        if(not exists(buildUp)):
            mkdir(buildUp)

@unittest.fixpath
def ismount(p):
    return os.path.ismount(p)

@unittest.fixpath
def fixpath(p):
    """This function is required because if we need to pass a path to something like tarfile,
        we cannot overwrite the function to fix the path, so we need to expose it somehow."""
    return p

@unittest.fixpath
def copy(a, b):
    return shutil.copy(a, b)

@unittest.fixpath
def move(a, b):
    return shutil.move(a, b)

@unittest.fixpath
def remove(a):
    if (isdir(a)):
        return shutil.rmtree(a)
    else:
        return os.remove(a)

@unittest.fixpath
def isdir(a):
    return os.path.isdir(a)

@unittest.fixpath
def isfile(a):
    return os.path.isfile(a)

@unittest.fixpath
def copytree(a, b):
    """shutil's copytree is dumb so use distutils."""
    return dir_util.copy_tree(a, b)

@unittest.fixopen
def open(p, mode):
    return __open(p, mode)

@unittest.fixpath
def makeExecutable(*args):
    """The function that takes the list of files provided and sets the X bit on them."""
    # Force args to be a tuple
    if(not (isinstance(args, list) or isinstance(args, tuple))):
        args = list(args)
   
    for a in args:
        out.verbose('-- %s Making %s executable\n' % (logPrefix(), os.path.basename(a)))
        
        if(os.path.exists(a)):
            os.chmod(a, 0744)
        else:
            out.warn('-- %s File missing "%s"\n' % (logPrefix(), a))

def writeFile(filename, line, mode="a"):
    """Adds the following cfg (either str or list(str)) to this Chute's current
        config file (just stored locally, not written to file."""
    try:
        if(type(line) is list):
            data = "\n".join(line) + "\n"
        elif(type(line) is str):
            data = "%s\n" % line
        else:
            out.err("!! Bad line provided for %s\n" % filename)
            return
        fd = open(filename, mode)
        fd.write(data)
        fd.flush()
        fd.close()

    except Exception as e:
        out.err('!! %s Unable to write file: %s\n' % (logPrefix(), str(e)))

def write(filename, data, mode="w"):
    """ Writes out a config file to the specified location.
    """
    try:
        fd = open(filename, mode)
        fd.write(data)
        fd.flush()
        fd.close()
    except Exception as e:
        out.err('!! Unable to write to file: %s\n' % str(e))

def readFile(filename, array=True, delimiter="\n"):
    """
        Reads in a file, the contents is NOT expected to be binary.
        Arguments:
            @filename: absolute path to file
            @array : optional: return as array if true, return as string if False
            @delimiter: optional: if returning as a string, this str specifies what to use to join the lines

        Returns:
            A list of strings, separated by newlines
            None: if the file doesn't exist
    """
    if(not exists(filename)):
        return None
    
    lines = []
    with open(filename, 'r') as fd:
        while(True):
            line = fd.readline()
            if(not line):
                break
            lines.append(line.rstrip())
    if(array is True):
        return lines
    else:
        return delimiter.join(lines)

