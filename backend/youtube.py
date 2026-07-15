import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")


def search_artist(artist):
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": API_KEY,
            "q": artist,
            "type": "channel",
            "part": "snippet",
            "maxResults": 1
        }
    )
    response.raise_for_status()
    return response.json()


def latest_uploads(channel_id):
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": API_KEY,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "type": "video",
            "maxResults": 10
        }
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    artist = "Beyoncé"

    channel = search_artist(artist)
    channel_id = channel["items"][0]["id"]["channelId"]

    print(f"\nArtist: {artist}")
    print(f"Channel: {channel['items'][0]['snippet']['title']}")
    print(f"Channel ID: {channel_id}\n")

    videos = latest_uploads(channel_id)

    for video in videos["items"]:
        title = video["snippet"]["title"]
        date = video["snippet"]["publishedAt"][:10]
        thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        video_id = video["id"]["videoId"]

        print("-----------------------------")
        print(title)
        print(date)
        print(thumbnail)
        print(f"https://youtube.com/watch?v={video_id}")