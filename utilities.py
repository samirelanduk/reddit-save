import os
import praw
import requests
from datetime import datetime
from secrets import REDDIT_USERNAME, REDDIT_PASSWORD
from secrets import REDDIT_CLIENT_ID, REDDIT_SECRET

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]
VIDEO_EXTENSIONS = ["mp4"]

def make_client():
    return praw.Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent="reddit-save",
    )


def get_saved_posts(client):
    for saved in client.user.me().saved(limit=None):
        if saved.__class__.__name__ == "Submission":
            yield saved


def get_upvoted_posts(client):
    for upvoted in client.user.me().upvoted(limit=None):
        if upvoted.__class__.__name__ == "Submission":
            yield upvoted


def get_post_html(post):
    with open(os.path.join("html", "post.html")) as f:
        html = f.read()
    dt = datetime.utcfromtimestamp(post.created_utc)
    html = html.replace("<!--title-->", post.title)
    html = html.replace("<!--subreddit-->", f"/r/{str(post.subreddit)}")
    html = html.replace("<!--user-->", f"/u/{post.author.name}" if post.author else "[deleted]")
    html = html.replace("<!--link-->", f"https://reddit.com{post.permalink}")
    html = html.replace("<!--content-link-->", post.url)
    html = html.replace("<!--body-->", post.selftext_html or "")
    html = html.replace("<!--timestamp-->", str(dt))
    html = html.replace("<!--date-->", dt.strftime("%d %B, %Y"))
    return html


def get_post_media(post):
    media_extensions = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS
    extension = post.url.split(".")[-1].lower()
    readable_name = list(filter(bool, post.permalink.split("/")))[-1]
    if extension in media_extensions:
        return {
            "name": f"{readable_name}_{post.id}.{extension}",
            "content": requests.get(post.url).content
        }

        # gyfcat, v.reddit, imgur, redgifs


def add_media_preview_to_html(post_html, media):
    extension = media["name"].split(".")[-1]
    location = "/".join(["media", media["name"]])
    if extension in IMAGE_EXTENSIONS:
        return post_html.replace(
            "<!--preview-->",
            f'<img src="{location}">'
        )
