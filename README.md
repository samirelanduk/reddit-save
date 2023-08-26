# reddit-save

A Python utility for backing up your reddit upvoted/saved stuff.

Browsing through the stuff you've liked or saved on reddit is really enjoyable and, depending on the reason you saved something, can be a great way to recap stuff you once thought important. It is a personalised feed of posts and comments by the one person guaranteed to know what you like - past you.

However over time more and more of the older posts will be deleted or missing, and the historical record atrophies. Use this tool to back up those posts and comments to your computer where you can browse them offline, and where they are safe forever.

reddit-save will backup saved posts, saved comments, and upvoted posts. It can't do upvoted comments because the reddit API doesn't expose them. Crucially, when it is run again on the same location it will ignore any posts/comments previously archived - once something is saved, it's saved permanently.

## Installation

```bash
$ git clone https://github.com/samirelanduk/reddit-save .
$ cd reddit-save
$ pip install -r requirements.txt
```

If you get permission errors, try using `sudo` or using a virtual environment.

You will need [ffmpeg](https://ffmpeg.org/) installed somewhere too.

Rename the file `logindata.py.example` to `logindata.py`. You will need to add four things to this file, your reddit username and password, and a reddit client ID and secret. The latter two are obtained using [the instructions here](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps). The file should look something like this:

```python
REDDIT_USERNAME = "spez"
REDDIT_PASSWORD = "myredditpassword123"
REDDIT_CLIENT_ID = "sadsU7-zfX"
REDDIT_SECRET = "687DDJSS&999d-hdkjK8h"
```

(If you have 2FA enabled, you will need to append that to the password, separated by a colon.)

## Use

Create a folder that will contain your archive. Then run:

```bash
$ ./save.py saved folder_name
$ ./save.py upvoted folder_name
```

The first command will backup your saved posts/comments to a file called folder_name/saved.html. The second will backup your upvoted posts to a file called folder_name/upvoted.html.

Each post will have its top-level comments saved, as well as each of their immediate child comments (but no further).

Linked media files (images, videos etc.) will be saved locally where possible, though imgur is currently not well supported in all cases.

If you want to also break the resultant HTML file into multiple files (as browsers struggle to display enormous HTML files) you can add the `--page-size 100` argument (replacing 100 with whatever the posts-per page you want is).

## Use with Docker

Rather than installing dependencies locally, you can use docker to create a local image and use that instead. First build the image:

```bash
$ docker build -t redditsave .
```

Then run reddit-save within a container created from this image:

```bash
$ docker run \
-e REDDIT_USERNAME=spez \
-e REDDIT_PASSWORD="myredditpassword123" \
-e REDDIT_CLIENT_ID="sadsU7-zfX" \
-e REDDIT_SECRET="687DDJSS&999d-hdkjK8h" \
-v /Local/location/to/save/in:/opt/app/archive \
redditsave saved
```

## Backing up a specific username

Rather than backing up your own saved/upvoted posts and comments, you can back up the submitted posts and comments of another user:

```bash
./save.py user:samirelanduk folder_name
```

## Backing up a specific username

Rather than backing up your own saved/upvoted posts and comments, you can back up the submitted posts and comments of another user:

```bash
./save.py user:samirelanduk folder_name
```