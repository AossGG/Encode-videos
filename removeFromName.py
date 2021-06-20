
import re
import os
import time
import argparse
from os import walk


def removeFromName(dir_path, reg):
    dirpath, dirnames, filenames = next(walk(dir_path))
    for directory in dirnames:
        removeFromName(directory, reg)
    
    for filename in filenames:
        newName = re.sub(reg, '', filename).strip()
        if(newName == ""): continue
        print(newName)
        os.rename(dirpath + "/" + filename, dirpath + "/" + newName)


parser = argparse.ArgumentParser(description='Convert to HEVC video encoder.')
parser.add_argument(
        '-r', '--regex', required=True, type=str, help='regex')
parser.add_argument(
        '-d', '--directory', required=True, type=str, help='directory path')

args = parser.parse_args()
regex = args.regex
dir_path = args.directory

removeFromName(dir_path, regex)
