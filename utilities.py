import os
import praw
import requests
from redvid import Downloader
import youtube_dl
import re
from datetime import datetime
from secrets import REDDIT_USERNAME, REDDIT_PASSWORD
from secrets import REDDIT_CLIENT_ID, REDDIT_SECRET

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "gifv"]
VIDEO_EXTENSIONS = ["mp4"]
PLATFORMS = ["redgifs.com", "gfycat.com", "imgur.com", "youtube.com"]

def make_client():
    """Creates a PRAW client with the details in the secrets.py file."""

    return praw.Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent="reddit-save",
    )


def get_saved_posts(client):
    """Gets a list of posts that the user has saved."""

    return [
        saved for saved in client.user.me().saved(limit=20)
        if saved.__class__.__name__ == "Submission"
    ]


def get_upvoted_posts(client):
    """Gets a list of posts that the user has saved."""

    return [
        upvoted for upvoted in client.user.me().upvoted(limit=None)
        if saved.__class__.__name__ == "Submission"
    ]


def get_post_html(post):
    """Takes a post object and creates a HTML for it - but not including the
    preview HTML."""

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
    """Takes a post object and tries to download any image/video it might be
    associated with. If it can, it will return the filename."""

    url = post.url
    stripped_url = url.split("?")[0]
    if url.endswith(post.permalink): return

    # What is the key information?
    extension = stripped_url.split(".")[-1].lower()
    domain = ".".join(post.url.split("/")[2].split(".")[-2:])
    readable_name = list(filter(bool, post.permalink.split("/")))[-1]

    # Can the media be obtained directly?
    if extension in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS:
        filename = f"{readable_name}_{post.id}.{extension}"
        with open(os.path.join(location, "media", filename), "wb") as f:
            response = requests.get(post.url)
            media_type = response.headers.get("Content-Type", "")
            if media_type.startswith("image") or media_type.startswith("video"):
                f.write(response.content)
                return filename
    
    # Is this a v.redd.it link?
    if domain == "redd.it":
        downloader = Downloader(max_q=True, log=False)
        downloader.url = url
        name = downloader.download()
        extension = name.split(".")[-1]
        filename = f"{readable_name}_{post.id}.{extension}"
        os.rename(name, os.path.join(location, "media", filename))
        return filename

    # Is it a gfycat link that redirects? Update the URL if possible
    if domain == "gfycat.com":
        html = requests.get(post.url).content
        if len(html) < 50000:
            match = re.search(r"http([\dA-Za-z\+\:\/\.]+)\.mp4", html.decode())
            if match:
                url = match.group()
            else: return None
    
    # Try to use youtube_dl if it's one of the possible domains
    if domain in PLATFORMS:
        options = {
            "nocheckcertificate": True, "quiet": True, "no_warnings": True,
            "ignoreerrors": True,
            "outtmpl": os.path.join(
                location, "media",  f"{readable_name}_{post.id}" + ".%(ext)s"
            )
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            try:
                ydl.download([url])
            except: pass
        for f in os.listdir(os.path.join(location, "media")):
            if f.startswith(f"{readable_name}_{post.id}"):
                return f


def add_media_preview_to_html(post_html, media):
    """Takes post HTML and returns a modified version with the preview
    inserted."""
    
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
    return post_html