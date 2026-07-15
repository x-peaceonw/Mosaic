import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

ARTISTS = ["Olivia Rodrigo", "Sondae", "Beyonce", "Taylor Swift", "Tori Kelly","Ariana Grande","Olivia Dean"]
TICKET_ARTISTS = ["Beyonce"]
NEWS_TOPICS = [
    {"query": "Zendaya fashion OR style OR outfit", "category": "Zendaya", "artist": "Zendaya"},
    {"query": "Beyonce", "category": "Beyonce News", "artist": "Beyonce"},
]

CUTOFF = datetime.now(timezone.utc) - timedelta(days=30)


# ---------- Spotify ----------

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


# ---------- YouTube ----------

def youtube_new_uploads(artist_name):
    search = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": YOUTUBE_API_KEY, "q": artist_name, "type": "channel",
            "part": "snippet", "maxResults": 1
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
            "key": YOUTUBE_API_KEY, "channelId": channel_id, "part": "snippet",
            "order": "date", "type": "video", "maxResults": 10
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


# ---------- Ticketmaster: Beyonce tour tickets ----------

def ticketmaster_events(artist_name):
    if not TICKETMASTER_API_KEY:
        return []
    response = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json",
        params={
            "apikey": TICKETMASTER_API_KEY,
            "keyword": artist_name,
            "sort": "date,asc",
            "size": 10
        }
    )
    response.raise_for_status()
    data = response.json()
    events = data.get("_embedded", {}).get("events", [])

    results = []
    for event in events:
        date_info = event.get("dates", {}).get("start", {})
        event_date = date_info.get("localDate", "TBA")
        images = event.get("images", [])
        image_url = images[0]["url"] if images else ""
        venue = ""
        try:
            venue = event["_embedded"]["venues"][0]["name"]
        except (KeyError, IndexError):
            pass

        results.append({
            "title": f"{event['name']}" + (f" — {venue}" if venue else ""),
            "artist": artist_name,
            "source": "Ticketmaster",
            "time": event_date,
            "image": image_url,
            "spotify": event["url"],
            "category": "Beyonce Tickets"
        })
    return results


# ---------- Google News RSS: Zendaya fashion, Beyonce news ----------

def google_news_rss(query, category, artist_name, limit=6):
    response = requests.get(
        "https://news.google.com/rss/search",
        params={"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"},
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall("./channel/item")[:limit]

    results = []
    for item in items:
        title = item.findtext("title", default="")
        link = item.findtext("link", default="")
        pub_date_raw = item.findtext("pubDate", default="")
        source_el = item.find("source")
        source = source_el.text if source_el is not None else "Google News"

        try:
            published = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        except ValueError:
            published = datetime.now(timezone.utc)

        if published < CUTOFF:
            continue

        results.append({
            "title": title,
            "artist": artist_name,
            "source": source,
            "time": published.strftime("%Y-%m-%d"),
            "image": "",
            "spotify": link,
            "category": category
        })
    return results


def main():
    all_posts = []

    try:
        token = get_spotify_token()
        for artist in ARTISTS:
            found = spotify_new_releases(artist, token)
            print(f"Spotify [{artist}]: {len(found)} items")
            all_posts.extend(found)
    except Exception as e:
        print(f"Spotify failed: {e}")

    for artist in ARTISTS:
        try:
            found = youtube_new_uploads(artist)
            print(f"YouTube [{artist}]: {len(found)} items")
            all_posts.extend(found)
        except Exception as e:
            print(f"YouTube [{artist}] failed: {e}")

    for artist in TICKET_ARTISTS:
        try:
            found = ticketmaster_events(artist)
            print(f"Ticketmaster [{artist}]: {len(found)} items")
            all_posts.extend(found)
        except Exception as e:
            print(f"Ticketmaster [{artist}] failed: {e}")

    for topic in NEWS_TOPICS:
        try:
            found = google_news_rss(topic["query"], topic["category"], topic["artist"])
            print(f"News [{topic['category']}]: {len(found)} items")
            all_posts.extend(found)
        except Exception as e:
            print(f"News [{topic['category']}] failed: {e}")

    all_posts.sort(key=lambda p: p["time"], reverse=True)

    os.makedirs("data", exist_ok=True)
    with open("data/music.json", "w") as f:
        json.dump(all_posts, f, indent=2)

    print(f"Wrote {len(all_posts)} items to data/music.json")


if __name__ == "__main__":
    main()
