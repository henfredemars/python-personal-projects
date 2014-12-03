#!/usr/bin/python3

#Rename folders to have simple, numeric names, and remove those problematic characters from my music library
#Different version to preserve folder names

#Warning! This script can potentially cause data loss! Be careful and make backups! NO WARRANTY

import os
import string
from time import sleep

dirContainingFolders = r'C:\Users\username\Music\My Music Library'
testRun = True

#Strictly speaking, not all punctuation is valid, but this will remove the problem chars
legalFileNameCharacters = (set(string.ascii_lowercase) |
                           set(string.ascii_uppercase) |
                           set(string.digits) |
                           set(string.punctuation) |
                           set(string.whitespace))

def main():

    for level in os.walk(dirContainingFolders):
        ldir = level[0]
        folders = level[1]
        files = level[2]
        join = lambda f:os.path.join(ldir,f)
        for folder in folders:
            newName = filterName(folder)
            if newName != folder and not os.path.exists(join(newName)):
                renamePrint(join(folder),join(newName))
        for fileName in files:
            newName = filterName(fileName)
            if fileName != newName and not os.path.exists(join(newName)):
                renamePrint(join(fileName),join(newName))
                
        #Update listing because we modified some names
        del folders[:]
        folders[:] = os.listdir(ldir)

def filterName(name):
    newName = name
    for char in name:
        if not char in legalFileNameCharacters:
            newName = newName.replace(char,"X")
    return newName

def renamePrint(src,dst):

    print("Changing {} to {}".format(src,dst))
    if not testRun:
        sleep(0.5)
        os.rename(src,dst)

if __name__=='__main__':
    main()
