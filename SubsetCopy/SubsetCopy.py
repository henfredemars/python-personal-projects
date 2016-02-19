#!/usr/bin/python3

import os
import random
import readline
import shutil
import time

#Copy a random subset of files from one directory tree into a new directory tree, emulating a
#	random partial rsync of two directory trees. This script was originally written to
#	randomly select from a subset of a music collection
#
#It is safe if the destination directory is part of the source tree. The files to be copied are
#	fully determined before the copying begins

#Default Settings

source_directory = None
dest_directory = None
max_files_copied = float('inf')
max_file_size = float('inf')
flatten_tree = True
filter_file_types = False

#Global Script Variables

files_copied = 0
file_types_allowed = []
total_bytes_copied = 0
start_time = time.time()
file_list = dict()

#Print Xfer Statistics
def print_stats():
  print("-"*30)
  print("Files Copied: {}.".format(files_copied))
  elapsed_seconds = start_time-time.time()
  minutes, seconds = divmod(elapsed_seconds, 60)
  print("Elapsed Time: {} minutes, {} seconds.".format(minutes,seconds))
  print("Bytes Copied: {}.".format(total_bytes_copied))

#User Interaction
def interact_user():
  #Explicitly attach to module variables
  global source_directory
  global dest_directory
  global max_files_copied
  global max_file_size
  global flatten_tree
  global filter_file_types

  print("Welcome to SubsetCopy!")
  print("Let's begin by configuring some settings.\n")
  inputs = lambda s: input(s).strip()
  source_directory_n = inputs("Source Directory [{}]: ".format(source_directory))
  dest_directory_n = inputs("Destination Directory [{}]: ".format(dest_directory))
  max_files_copied_n = inputs("Maximum number of files to copy [{}]: "
    .format(max_files_copied))
  max_file_size_n = inputs("Maximum file size (bytes) for each copy [{}]: "
    .format(max_file_size))
  flatten_tree_n = inputs("Flatten file tree after copy? [{}]: "
    .format(flatten_tree))
  filter_file_types_n = inputs("Filter file types? [{}]: ".format(filter_file_types))

  #Implement default values
  user_truth_bool = lambda s: (s.lower()!="no" and s.lower()!="false") and bool(s)
  if source_directory_n:
    source_directory = source_directory_n
  if dest_directory_n:
    dest_directory = dest_directory_n
  if max_files_copied_n:
    max_files_copied = float(max_files_copied_n)
  if max_file_size_n:
    max_file_size = float(max_file_size_n)
  if flatten_tree_n:
    flatten_tree = user_truth_bool(flatten_tree_n)
  if filter_file_types_n:
    filter_file_types = user_truth_bool(filter_file_types_n)

  #Check for valid paths and expand into full paths
  assert os.path.exists(source_directory), "Invalid source directory"
  source_directory = os.path.abspath(source_directory)
  dest_directory = os.path.abspath(dest_directory)

  #Configure the file type filter if needed
  if filter_file_types:
    ftype = True
    while ftype:
      ftype = inputs("Enter file type to include [Finish]: ")
      if not ftype:
        break
      if not '.' in ftype:
        ftype = '.' + ftype
      file_types_allowed.append(ftype)

#Populate the file list, filtering out files that have the wrong type or are too large
def populate_file_list():
  print("Populating file list...")
  for (dirpath, dirnames, filenames) in os.walk(source_directory):
    if filter_file_types:
      filenames = [name for name in filenames if name.endswith(tuple(file_types_allowed))]
    [file_list.setdefault(os.path.join(dirpath,name),None) for name in filenames if 
      os.path.getsize(os.path.join(dirpath,name)) <= max_file_size]

#Determine and fill-in the destination paths
def transform_file_list():
  for path in file_list:
    if flatten_tree:
      file_list[path] = os.path.join(dest_directory,os.path.basename(path))
    else:
      file_list[path] = os.path.join(dest_directory,path.strip(os.sep))

#Copy the files, being careful not to overwrite and update statistics
def copy_carefully():
  global files_copied
  global total_bytes_copied
  while files_copied < max_files_copied:
    spath = random.choice(list(file_list.keys()))
    dpath = file_list[spath]
    if os.path.isfile(dpath):
      dst_candidate_path = dpath
      dup_counter = 1
      while os.path.isfile(dst_candidate_path):
        bname = os.path.basename(dst_candidate_path)
        if '.' in bname:
          sname,ext = bname.split('.')
        else:
          sname = bname
          ext = ''
        sname += " - {}".format(dup_counter)
        dst_candidate_path = os.path.join(os.path.dirname(dst_candidate_path),sname+ext)
      dpath = file_list[spath] = dst_candidate_path
      assert not os.path.isfile(dst_candidate_path), "Shouldn't happen!"
    try:
      print("{} => {}".format(spath,dpath))
      dest_dirpath = os.path.dirname(dpath)
      if not os.path.exists(dest_dirpath):
        os.makedirs(dest_dirpath)
      shutil.copyfile(spath,dpath)
      del file_list[spath]
    except IOError:
      print("Error recieved from device. Probably the device is full.")
      os.remove(dpath)
      break
    files_copied += 1
    total_bytes_copied += os.path.getsize(dpath)

#Main
def main():
  interact_user()
  populate_file_list()
  transform_file_list()
  copy_carefully()
  print_stats()

#Run script text if script is not being imported
if __name__=='__main__':
  print("I'm main!")
  main()
  print("All operations have concluded.")
