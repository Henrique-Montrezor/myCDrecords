import os
import time
import base64
import requests
try:
    import certifi
    CA_BUNDLE = certifi.where()
except Exception:
    CA_BUNDLE = True

_token = None
_token_expires = 0

def get_spotify_token():
    global _token, _token_expires
    if _token and time.time() < _token_expires - 60:
        return _token
    # Read credentials at call time (handles case where .env is loaded after module import)
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    if not client_id or not client_secret:
        raise RuntimeError('Spotify credentials not configured')
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = requests.post('https://accounts.spotify.com/api/token',
                         data={'grant_type':'client_credentials'},
                         headers={'Authorization': f'Basic {auth}'},
                         verify=CA_BUNDLE)
    resp.raise_for_status()
    data = resp.json()
    _token = data['access_token']
    _token_expires = time.time() + data.get('expires_in', 3600)
    return _token

def search_albums(query, limit=10):
    token = get_spotify_token()
    resp = requests.get('https://api.spotify.com/v1/search',
                        headers={'Authorization': f'Bearer {token}'},
                        params={'q': query, 'type': 'album', 'limit': limit},
                        verify=CA_BUNDLE)
    resp.raise_for_status()
    return resp.json().get('albums', {}).get('items', [])

def get_album(album_id):
    token = get_spotify_token()
    resp = requests.get(f'https://api.spotify.com/v1/albums/{album_id}',
                        headers={'Authorization': f'Bearer {token}'},
                        verify=CA_BUNDLE)
    resp.raise_for_status()
    return resp.json()


def get_new_releases(limit=10, country=None):
    """Return list of new release albums from Spotify Browse endpoint.
    Returns the list of album items (same structure as search_albums items).
    """
    token = get_spotify_token()
    params = {'limit': limit}
    if country:
        params['country'] = country
    resp = requests.get('https://api.spotify.com/v1/browse/new-releases',
                        headers={'Authorization': f'Bearer {token}'},
                        params=params,
                        verify=CA_BUNDLE)
    resp.raise_for_status()
    data = resp.json()
    # structure: {'albums': {'href':..., 'items': [...]}}
    return data.get('albums', {}).get('items', [])

def get_recommendations(seed_artists=None, seed_tracks=None, limit=10):
    token = get_spotify_token()
    params = {'limit': limit}
    if seed_artists:
        params['seed_artists'] = ','.join(seed_artists)
    if seed_tracks:
        params['seed_tracks'] = ','.join(seed_tracks)
    resp = requests.get('https://api.spotify.com/v1/recommendations',
                        headers={'Authorization': f'Bearer {token}'},
                        params=params,
                        verify=CA_BUNDLE)
    resp.raise_for_status()
    return resp.json().get('tracks', [])
