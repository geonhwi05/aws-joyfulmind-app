import requests

# Spotify API 인증 함수
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

# 추천 노래 가져오기 함수
def recommend_songs(emotion, limit=10):
    client_id = 'cd2f26006026488e8890107fa77c8042'
    client_secret = '409e4304e723414faa5253137febbdc6'
    token = get_spotify_token(client_id, client_secret)
    
    # 시드값 정의
    seed_data = {
        '슬픔': {
            'seed_artists': ['6HvZYsbFfjnjFrWF950C9d', '1wEoc7wT6O4Xf4Fczcd6zH'],  # Example: 'BTS', 'IU'
            'seed_tracks': ['5qaEfEh1AtSdrdrByCP7qR', '3yfqSUWxFvZELEM4PmlwIR']  # Example: 'Spring Day', 'Eight'
        },
        '기쁨': {
            'seed_artists': ['6nfDaffa50mKtEOwR8g4df', '3Nrfpe0tUJi4K4DXYWgMUX'],  # Example: 'TWICE', 'EXO'
            'seed_tracks': ['2FgVBd2INHSzH2diSi1vKq', '4K3EGRZgYK2Qb1WT6BmGpm']  # Example: 'Dance The Night Away', 'Love Shot'
        },
        '분노': {
            'seed_artists': ['1z4g3DjTBBZKhvAroFlhOM', '3Nrfpe0tUJi4K4DXYWgMUX'],  # Example: 'Stray Kids', 'EXO'
            'seed_tracks': ['1eFakWZFFjbI3uD6udlD7G', '4XUlx2tFhbL3eGn86ZYlYf']  # Example: 'God's Menu', 'Monster'
        },
        '공포': {
            'seed_artists': ['2hcsKca6hCfFMwwdbFvenJ', '5eibyscprKO85rm36Yaq7B'],  # Example: 'Dreamcatcher', 'ATEEZ'
            'seed_tracks': ['3YdL89w55i1tU2vxVhL01y', '2LRoIwlFukmyCjuyudHc76']  # Example: 'Scream', 'Wonderland'
        },
        '놀람': {
            'seed_artists': ['5dCvSnVduaFleCnyy98JMo', '1wEoc7wT6O4Xf4Fczcd6zH'],  # Example: 'EXO', 'IU'
            'seed_tracks': ['7lFh1J3U90rVYAHNdOXzMM', '1AJe3A5nEWI3HxkPeBdj0Y']  # Example: 'Love Shot', 'BBIBBI'
        },
        '극혐': {
            'seed_artists': ['6rQeXFCcNckj3Lb5j0wHzV', '2dIgFjalVxs4ThymZ67YCE'],  # Example: 'BLACKPINK', 'Red Velvet'
            'seed_tracks': ['2YZyLoL8N0Wb9xBt1NhZWg', '3Kkjo3cT83cw09VJyrLNwX']  # Example: 'How You Like That', 'Psycho'
        }
    }
    
    seeds = seed_data.get(emotion)
    
    if not seeds:
        return []
    
    recommend_url = 'https://api.spotify.com/v1/recommendations'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'seed_artists': ','.join(seeds['seed_artists']),
        'seed_tracks': ','.join(seeds['seed_tracks']),
        'seed_genres': 'k-pop',
        'limit': 50  # 더 많은 곡을 가져와서 필터링하기 위해
    }
    
    response = requests.get(recommend_url, headers=headers, params=params)
    tracks = response.json().get('tracks', [])
    
    songs = []
    for track in tracks:
        if track['preview_url']:  # 미리듣기 URL이 있는 경우만 포함
            song = {
                'name': track['name'],
                'artists': ', '.join([artist['name'] for artist in track['artists']]),
                'preview_url': track['preview_url'],
                'album_cover_url': track['album']['images'][0]['url']
            }
            songs.append(song)
        if len(songs) >= limit:  # 원하는 개수만큼 채우면 종료
            break
    
    return songs
