import os
import praw
import requests
import youtube_dl
import re
from datetime import datetime
from secrets2 import REDDIT_USERNAME, REDDIT_PASSWORD
from secrets2 import REDDIT_CLIENT_ID, REDDIT_SECRET

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]
VIDEO_EXTENSIONS = ["mp4"]
PLATFORMS = ["redgifs.com", "gfycat.com"]

def make_client():
    return praw.Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent="reddit-save",
    )


def get_saved_posts(client):
    return [
        saved for saved in client.user.me().saved(limit=10)
        if saved.__class__.__name__ == "Submission"
    ]


def get_upvoted_posts(client):
    return [
        upvoted for upvoted in client.user.me().upvoted(limit=None)
        if saved.__class__.__name__ == "Submission"
    ]


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


def save_media(post, location):
    media_extensions = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS
    extension = post.url.split(".")[-1].lower()
    readable_name = list(filter(bool, post.permalink.split("/")))[-1]
    if extension in media_extensions:
        filename = f"{readable_name}_{post.id}.{extension}"
        with open(os.path.join(location, "media", filename), "wb") as f:
            f.write(requests.get(post.url).content)
            return filename
    else:
        domain = ".".join(post.url.split("/")[2].split(".")[-2:])
        if domain in PLATFORMS:
            url = post.url
            if domain == "gfycat.com":
                html = requests.get(post.url).content
                if len(html) < 50000:
                    match = re.search(
                        r"http([\dA-Za-z\+\:\/\.]+)\.mp4", html.decode()
                    )
                    if match:
                        url = match.group()
                    else: return None
            options = {
                "nocheckcertificate": True, "quiet": True, "no_warnings": True,
                "outtmpl": os.path.join(
                    location, "media",  f"{readable_name}_{post.id}" + ".%(ext)s"
                )
            }
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([url])
            for f in os.listdir(os.path.join(location, "media")):
                if f.startswith(f"{readable_name}_{post.id}"):
                    return f

        # gyfcat, v.reddit, imgur, redgifs


def add_media_preview_to_html(post_html, media):
    extension = media.split(".")[-1]
    location = "/".join(["media", media])
    if extension in IMAGE_EXTENSIONS:
        return post_html.replace(
            "<!--preview-->",
            f'<img src="{location}">'
        )
    if extension in VIDEO_EXTENSIONS:
        return post_html.replace(
            "<!--preview-->",
            f'<video controls><source src="{location}"></video>'
        )