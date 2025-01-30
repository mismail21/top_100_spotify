from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os


# Load the .env file
load_dotenv()

# Get credentials from .env file
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_username = os.getenv("SPOTIFY_USERNAME")


# Header to avoid bot detection
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}

# Get user input for date
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

# Corrected URL
url = f"https://www.billboard.com/charts/hot-100/{date}"
response = requests.get(url, headers=header)
website_html = response.text

# Parse Billboard page
soup = BeautifulSoup(website_html, "html.parser")
song_names_spans = soup.select("li ul li h3")

# Extract song names
song_names = [song.getText().strip() for song in song_names_spans]
print("Extracted Songs:", song_names)  # Debugging print statement



# Authenticate with Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://example.com",
        client_id=client_id,
        client_secret=client_secret,
        show_dialog=True,
        cache_path="token.txt",
        username=spotify_username
    )
)

# Get current user ID
user_id = sp.current_user()["id"]
print("Spotify User ID:", user_id)

# Find songs on Spotify
song_uris = []
year = date.split("-")[0]

for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print("Spotify Search Result:", result)  # Debugging print statement

    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Check if songs were found before proceeding
if not song_uris:
    print("No songs found on Spotify. Check the search query.")
    exit()

# Create a new private playlist
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print("Playlist Created:", playlist["external_urls"]["spotify"])

# Add songs to playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
print("Songs added successfully!")
