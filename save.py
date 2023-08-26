#!/usr/bin/env python 

import argparse
import os
import re
from tqdm import tqdm
from utilities import *

# Get arguments
def validate_mode(mode):
    if mode not in ["saved", "upvoted"] and not mode.startswith("user:"):
        raise argparse.ArgumentTypeError(f"Invalid mode: {mode}")
    return mode
parser = argparse.ArgumentParser(description="Save reddit posts to file.")
parser.add_argument("mode", type=validate_mode, nargs=1, help="The file to convert.")
if os.getenv("DOCKER", "0") != "1":
    parser.add_argument("location", type=str, nargs=1, help="The path to save to.")
# Optional page size argument
parser.add_argument("--page-size", type=int, nargs=1, default=[0], help="The number of posts to save per page.")
args = parser.parse_args()
mode = args.mode[0]
page_size = args.page_size[0]
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
elif mode == "upvoted":
    html_file = "upvoted.html"
    get_posts = get_upvoted_posts
    get_comments = lambda client: []
elif mode.startswith("user:"):
    username = mode.split(":")[-1]
    html_file = f"{username}.html"
    get_posts = lambda client: get_user_posts(client, username)
    get_comments = lambda client: get_user_comments(client, username)

# Make directory for media and posts
if not os.path.exists(os.path.join(location, "media")):
    os.mkdir(os.path.join(location, "media"))
if not os.path.exists(os.path.join(location, "posts")):
    os.mkdir(os.path.join(location, "posts"))

# Get files to search through
print("Getting previously saved posts and comments...")
existing_ids, existing_posts_html, existing_comments_html = get_previous(location, html_file)
print(len(existing_posts_html), "previous posts.")
print(len(existing_comments_html), "previous comments.")

# Get posts HTML
posts_html = []
posts = [p for p in get_posts(client) if p.id not in existing_ids]
if not posts:
    print("No new posts")
else:
    for post in tqdm(posts):
        post_html = get_post_html(post)
        media = save_media(post, location)
        if media:
            post_html = add_media_preview_to_html(post_html, media)
        posts_html.append(post_html)
        page_html = create_post_page_html(post, post_html)
        with open(os.path.join(location, "posts", f"{post.id}.html"), "w", encoding="utf-8") as f:
            f.write(page_html)
posts_html += existing_posts_html

# Get comments HTML
comments_html = []
comments = [c for c in get_comments(client) if c.id not in existing_ids]
if not comments:
    print("No new comments")
else:
    for comment in tqdm(comments):
        comment_html = get_comment_html(comment)
        media = save_media(post, location)
        comments_html.append(comment_html)
comments_html += existing_comments_html

# Save overall HTML
print("Saving HTML...")
if page_size:
    length = max(len(posts_html), len(comments_html))
    page_count = (length // page_size) + 1
    for i in range(page_count):
        posts_on_page = posts_html[i*page_size:(i+1)*page_size]
        comments_on_page = comments_html[i*page_size:(i+1)*page_size]
        has_next = i < page_count - 1
        save_html(posts_on_page, comments_on_page, location, html_file, i, has_next, username=html_file.split(".")[0])
save_html(posts_html, comments_html, location, html_file, None, False, username=html_file.split(".")[0])
