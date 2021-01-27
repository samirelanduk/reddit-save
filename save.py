#!/usr/bin/env python 

import argparse
import os
import re
from tqdm import tqdm
from utilities import *

# Get arguments
parser = argparse.ArgumentParser(description="Save reddit posts to file.")
parser.add_argument("mode", type=str, nargs=1, choices=["saved", "upvoted"], help="The file to convert.")

if os.getenv("DOCKER", "0") != "1":
    parser.add_argument("location", type=str, nargs=1, help="The path to save to.")
args = parser.parse_args()
mode = args.mode[0]
location = "./archive/" if os.getenv("DOCKER", "0") == "1" else args.location[0]

# Is location specified a directory?
if not os.path.isdir(location):
    print(location, "is not a directory")

# Make a client object
client = make_client()

# Saved posts or upvoted posts?
if mode == "saved":
    html_file = "saved.html"
    get_posts = get_saved_posts
    get_comments = get_saved_comments
else:
    html_file = "upvoted.html"
    get_posts = get_upvoted_posts
    get_comments = lambda client: []

# Make directory for media and posts
if not os.path.exists(os.path.join(location, "media")):
    os.mkdir(os.path.join(location, "media"))
if not os.path.exists(os.path.join(location, "posts")):
    os.mkdir(os.path.join(location, "posts"))

# Are there any posts already?
post_ids, existing_posts_html = [], []
if os.path.exists(os.path.join(location, html_file)):
    with open(os.path.join(location, html_file)) as f:
        current_html = f.read()
        post_ids = re.findall(r'id="(.+?)"', current_html)
        existing_posts_html = re.findall(
            r'(<div class="post"[\S\n\t\v ]+?<!--postend--><\/div>)',
            current_html
        )

# Get posts HTML
posts_html = []
posts = [p for p in get_posts(client) if p.id not in post_ids]
if not posts:
    print("No new saved posts")
else:
    for post in tqdm(posts):
        post_html = get_post_html(post)
        media = save_media(post, location)
        if media:
            post_html = add_media_preview_to_html(post_html, media)
        posts_html.append(post_html)
        page_html = create_post_page_html(post, post_html)
        with open(os.path.join(location, "posts", f"{post.id}.html"), "w") as f:
            f.write(page_html)
posts_html += existing_posts_html

# Are there any comments already?
comment_ids, existing_comments_html = [], []
if os.path.exists(os.path.join(location, html_file)):
    with open(os.path.join(location, html_file)) as f:
        current_html = f.read()
        comment_ids = re.findall(r'id="(.+?)"', current_html)
        existing_comments_html = re.findall(
            r'(<div class="comment"[\S\n\t\v ]+?<!--commentend--><\/div>)',
            current_html
        )

# Get comments HTML
comments_html = []
comments = [c for c in get_comments(client) if c.id not in comment_ids]
if not comments:
    print("No new saved comments")
else:
    for comment in tqdm(comments):
        comment_html = get_comment_html(comment)
        media = save_media(post, location)
        comments_html.append(comment_html)
comments_html += existing_comments_html

# Save HTML
with open(os.path.join("html", html_file)) as f:
    html = f.read()
with open(os.path.join("html", "style.css")) as f:
    html = html.replace("<style></style>", f"<style>\n{f.read()}\n</style>")
with open(os.path.join("html", "main.js")) as f:
    html = html.replace("<script></script>", f"<script>\n{f.read()}\n</script>")
html = html.replace("<!--posts-->", "\n".join(posts_html))
html = html.replace("<!--comments-->", "\n".join(comments_html))
with open(os.path.join(location, html_file), "w") as f:
    f.write(html)


