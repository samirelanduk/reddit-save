import os
import praw
from datetime import datetime
from secrets import REDDIT_USERNAME, REDDIT_PASSWORD
from secrets import REDDIT_CLIENT_ID, REDDIT_SECRET

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
    html = html.replace("<!--timestamp-->", str(dt))
    html = html.replace("<!--date-->", dt.strftime("%d %B, %Y"))
    return html