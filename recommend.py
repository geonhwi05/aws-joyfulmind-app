import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API 인증 설정
client_id = 'cd2f26006026488e8890107fa77c8042'
client_secret = '409e4304e723414faa5253137febbdc6'
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def recommend_songs(emotion, limit=10):
    results = sp.search(q=emotion, type='track', limit=limit)
    songs = []
    for track in results['tracks']['items']:
        song = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'url': track['external_urls']['spotify'],
            'thumbnail': track['album']['images'][0]['url']  # 앨범 이미지의 URL을 가져옵니다.
        }
        songs.append(song)
    return songs
