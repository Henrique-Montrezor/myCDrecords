import requests

# Token de autorização (deve ser gerado previamente)
token = "BQB9IMP-Jte5OyNDp7kWV01tqG0c2fqtWWLl1HDw6faQLm7u-T--vuoXh49fCkKWxv1tqPPaBz51rrUbyuFuvBdC0AVS_8LeJADCxsy5M3ABqqhTWgrLvn9rhFRnZ-bYqX9rDAUP7kBRKerz60aQrui7pznBNC5VONZL7XYbkD7qyvGlqQnX803eRBX1V7wYJwulbXwf4k3lmrdNDqsr-i9kvFaFerv7zD7IJzPQneHZyfX1Ao6Lu9wRxR4jNldnK7k-Je-8C8ZwPBKx6OS7i2PzCngVQBY0BwMWaKiur3JXCg"

BASE_URL = "https://api.spotify.com/"

def fetch_web_api(endpoint, method="GET", body=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.request(method, url, headers=headers, json=body)
    response.raise_for_status()  # Lança erro se a requisição falhar
    return response.json()

def get_top_tracks():
    # Referência do endpoint: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    endpoint = "v1/me/top/tracks?time_range=long_term&limit=5"
    data = fetch_web_api(endpoint)
    return data.get("items", [])

if __name__ == "__main__":
    top_tracks = get_top_tracks()
    print("Suas 5 músicas mais ouvidas:")
    for i, track in enumerate(top_tracks, start=1):
        name = track["name"]
        artists = ", ".join(artist["name"] for artist in track["artists"])
        print(f"{i}. {name} - {artists}")