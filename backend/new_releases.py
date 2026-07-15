import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


ARTISTS = [
    "Beyoncé",
    "Ariana Grande",
    "Olivia Rodrigo"
]


def get_token():

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type":"client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )

    response.raise_for_status()

    return response.json()["access_token"]


def get_artist_id(name, token):

    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={
            "Authorization":f"Bearer {token}"
        },
        params={
            "q":name,
            "type":"artist",
            "limit":1
        }
    )

    response.raise_for_status()

    return response.json()["artists"]["items"][0]["id"]


def get_albums(artist_id, token):

    response = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}/albums",
        headers={
            "Authorization":f"Bearer {token}"
        },
        params={
            "include_groups":"album,single",
            "limit":10
        }
    )

    response.raise_for_status()

    return response.json()["items"]


token = get_token()

today = datetime.today()

cards = []

for artist in ARTISTS:

    artist_id = get_artist_id(artist, token)

    albums = get_albums(artist_id, token)

    for album in albums:

        if len(album["release_date"]) != 10:
            continue

        release = datetime.strptime(
            album["release_date"],
            "%Y-%m-%d"
        )

        if release.month == today.month and release.year == today.year:

            cards.append({

                "id":album["id"],

                "category":"Music",

                "artist":artist,

                "title":album["name"],

                "source":"Spotify",

                "time":album["release_date"],

                "image":album["images"][0]["url"],

                "spotify":album["external_urls"]["spotify"]

            })

os.makedirs("frontend/data", exist_ok=True)

with open("frontend/data/music.json","w") as f:

    json.dump(cards,f,indent=4)

print("Created frontend/data/music.json")