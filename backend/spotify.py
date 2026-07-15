import os
import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_token():
    """Request a Spotify API access token."""
    url = "https://accounts.spotify.com/api/token"

    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    response.raise_for_status()
    return response.json()["access_token"]


def search_artist(artist_name):
    """Search Spotify for an artist."""
    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params={
            "q": artist_name,
            "type": "artist",
            "limit": 1
        }
    )
    response.raise_for_status()
    return response.json()


def get_artist(artist_name):
    """Return only the data Mosaic needs."""
    result = search_artist(artist_name)
    artist = result["artists"]["items"][0]

    return {
        "name": artist["name"],
        "followers": artist["followers"]["total"],
        "popularity": artist["popularity"],
        "image": artist["images"][0]["url"],
        "spotify": artist["external_urls"]["spotify"]
    }


if __name__ == "__main__":
    artists = [
        "Olivia Rodrigo",
        "SZA",
        "Beyoncé",
        "Taylor Swift",
        "Bad Bunny"
    ]

    for name in artists:
        artist = get_artist(name)

        print("------------------------------")
        print(f"Artist: {artist['name']}")
        print(f"Followers: {artist['followers']:,}")
        print(f"Popularity: {artist['popularity']}/100")
        print(f"Spotify: {artist['spotify']}")
        print(f"Image: {artist['image']}")