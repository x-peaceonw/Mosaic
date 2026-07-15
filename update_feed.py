import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Edit this list to whoever you actually want to follow
ARTISTS = ["Olivia Rodrigo", "SZA", "Beyoncé", "Taylor Swift", "Bad Bunny"]

CUTOFF = datetime.now(timezone.utc) - timedelta(days=30)


def get_spotify_token():
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    )
    response.raise_for_status()
    return response.json()["access_token"]


def spotify_new_releases(artist_name, token):
    headers = {"Authorization": f"Bearer {token}"}

    search = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params={"q": artist_name, "type": "artist", "limit": 1}
    )
    search.raise_for_status()
    items = search.json()["artists"]["items"]
    if not items:
        return []
    artist_id = items[0]["id"]

    albums = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}/albums",
        headers=headers,
        params={"include_groups": "single,album", "limit": 10}
    )
    albums.raise_for_status()

    results = []
    for album in albums.json()["items"]:
        release_date = album["release_date"]
        try:
            released = datetime.strptime(release_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            released = datetime.strptime(release_date, "%Y").replace(tzinfo=timezone.utc)

        if released < CUTOFF:
            continue

        results.append({
            "title": album["name"],
            "artist": artist_name,
            "source": "Spotify",
            "time": release_date,
            "image": album["images"][0]["url"] if album["images"] else "",
            "spotify": album["external_urls"]["spotify"],
            "category": "Music"
        })
    return results


def youtube_new_uploads(artist_name):
    search = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": YOUTUBE_API_KEY,
            "q": artist_name,
            "type": "channel",
            "part": "snippet",
            "maxResults": 1
        }
    )
    search.raise_for_status()
    items = search.json()["items"]
    if not items:
        return []
    channel_id = items[0]["id"]["channelId"]

    uploads = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": YOUTUBE_API_KEY,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "type": "video",
            "maxResults": 10
        }
    )
    uploads.raise_for_status()

    results = []
    for video in uploads.json()["items"]:
        published = datetime.strptime(
            video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)

        if published < CUTOFF:
            continue

        results.append({
            "title": video["snippet"]["title"],
            "artist": artist_name,
            "source": "YouTube",
            "time": published.strftime("%Y-%m-%d"),
            "image": video["snippet"]["thumbnails"]["high"]["url"],
            "spotify": f"https://youtube.com/watch?v={video['id']['videoId']}",
            "category": "Music"
        })
    return results


def main():
    token = get_spotify_token()
    all_posts = []

    for artist in ARTISTS:
        all_posts.extend(spotify_new_releases(artist, token))
        all_posts.extend(youtube_new_uploads(artist))

    all_posts.sort(key=lambda p: p["time"], reverse=True)

    os.makedirs("data", exist_ok=True)
    with open("data/music.json", "w") as f:
        json.dump(all_posts, f, indent=2)

    print(f"Wrote {len(all_posts)} new releases (last 30 days) to data/music.json")


if __name__ == "__main__":
    main()
