#!/usr/bin/env python
"""
Test script: chama `spotify_client.search_albums` diretamente.
Como usar:
  1. Crie um venv e instale `pip install -r requirements.txt`.
  2. Adicione `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` no seu `.env` ou variáveis de ambiente.
  3. Rode: `python test_search_spotify.py "pink floyd"`
"""
import sys
from dotenv import load_dotenv
import os

load_dotenv()

from spotify_client import search_albums


def main():
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "beatles"
    print(f"Buscando álbuns para query: '{query}'")
    try:
        items = search_albums(query, limit=10)
        print(f"Recebidos {len(items)} resultados")
        for i, it in enumerate(items, start=1):
            artists = ', '.join([a.get('name') for a in it.get('artists', [])])
            name = it.get('name')
            aid = it.get('id')
            print(f"{i}. {name} — {artists} (id:{aid})")
    except Exception as e:
        print("Erro ao buscar álbuns:", e)


if __name__ == '__main__':
    main()
