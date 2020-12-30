#!/usr/bin/env python 

import argparse
import os

# Get arguments
parser = argparse.ArgumentParser(description="Save reddit posts to file.")
parser.add_argument("mode", type=str, nargs=1, choices=["saved", "upvoted"], help="The file to convert.")
parser.add_argument("location", type=str, nargs=1, help="The path to save to.")
args = parser.parse_args()
mode = args.mode[0]
location = args.location[0]

# Is location specified a directory?
if not os.path.isdir(location):
    print(location, "is not a directory")