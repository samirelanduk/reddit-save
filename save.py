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

if mode == "saved":
    html_file = "saved.html"
    get_posts = get_saved_posts
else:
    html_file = "upvoted.html"
    get_posts = get_upvoted_posts

posts_html = []

for post in get_posts(client):
    posts_html.append(get_post_html(post))

with open(os.path.join("html", html_file)) as f:
    html = f.read()

with open(os.path.join("html", "style.css")) as f:
    html = html.replace("<style></style>", f"<style>\n{f.read()}\n</style>")

html = html.replace("<!--posts-->", "\n".join(posts_html))

with open(os.path.join(location, html_file), "w") as f:
    f.write(html)



'''for post in get_saved_posts(client):
    print(post.title)'''