#!/usr/bin/env python 

import argparse
import os
from utilities import *

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

# Make a client object
client = make_client()

posts_html = []

for post in get_saved_posts(client):
    posts_html.append(get_post_html(post))

with open(os.path.join("html", "saved.html")) as f:
    html = f.read()

html = html.replace("<!--posts-->", "\n".join(posts_html))

with open(os.path.join(location, "saved.html"), "w") as f:
    f.write(html)



'''for post in get_saved_posts(client):
    print(post.title)'''