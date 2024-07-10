from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests
import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIFY_USERNAME = os.getenv("SPOTIFY_USERNAME")

# ----------------- SETTING-UP SPOTIFY AUTH WITH SPOTIPY -----------------------------------

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        client_id=SPOTIPY_CLIENT_ID,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        client_secret=SPOTIPY_CLIENT_SECRET,
        username=SPOTIFY_USERNAME,
        show_dialog=True,
        cache_path="token.txt",
    )
)

user_id = sp.current_user()["id"]

# ----------------- SCRAPING BILLBOARD USING BEAUTIFUL SOUP ----------------------------------- #

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
url = f"https://www.billboard.com/charts/hot-100/{date}/"

response = requests.get(url)
songs_list = response.text
soup = BeautifulSoup(songs_list, "html.parser")

top_100_titles = soup.select("li ul li h3")

# [new_item for item in list]
songs = [song.getText().strip("\n\t") for song in top_100_titles]

# ----------------- SEARCH SPOTIFY FOR THE SCRAPED SONGS ----------------------------------- #

song_uris = []

year = date.split("-")[0]

for song in songs:
    results = sp.search(q=f"track: {song} year: {year}", type="track")
    try:
        uri = results['tracks']['items'][0]['uri']
        song_uris.append(uri)
    except IndexError:
        print(f"Song {song} doesn't exist in Spotify. Skipped")


# ----------------- CREATE PLAYLIST ----------------------------------- #


playlist = sp.user_playlist_create(
    user=SPOTIFY_USERNAME, name=f'{date} Billboard 100', public=False)

sp.playlist_add_items(
    playlist_id=playlist['id'], items=song_uris)






