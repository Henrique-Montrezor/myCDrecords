#!/usr/bin/env python
"""
Test script: registra (se necessário), faz login e chama a rota `/api/search_album`.
Requisitos:
  - O servidor Flask deve estar rodando: `python app.py` (porta 5000 por padrão).
  - Variáveis de ambiente/arquivo `.env` com `SECRET_KEY` e credenciais do Spotify se quiser fallback.

Como usar:
  1. Ative venv e instale dependências.
  2. Rode o servidor: `python app.py` (num terminal separado).
  3. Em outro terminal rode: `python test_api_search.py "pink floyd"`

O script tentará registrar um usuário de teste `test_api_user` (se já existir, seguirá para login).
"""
import sys
import time
from dotenv import load_dotenv
import os
import requests

load_dotenv()

BASE = os.environ.get('APP_BASE_URL', 'http://127.0.0.1:5000')

USERNAME = 'test_api_user'
EMAIL = 'test_api_user@example.com'
PASSWORD = 'testpass123'


def register_if_needed(session):
    # Tenta registrar (se já existir, a app apenas exibirá mensagem e não quebrará)
    reg_url = f"{BASE}/registrar"
    print('Tentando registrar usuário de teste (pode já existir) ...')
    resp = session.post(reg_url, data={
        'username': USERNAME,
        'email': EMAIL,
        'password': PASSWORD
    }, allow_redirects=True)
    print('Registro status:', resp.status_code)


def login(session):
    login_url = f"{BASE}/login"
    print('Fazendo login...')
    resp = session.post(login_url, data={'email': EMAIL, 'password': PASSWORD}, allow_redirects=True)
    print('Login status:', resp.status_code)
    # Verifica se cookie de sessão foi recebido
    if 'session' in session.cookies.get_dict() or session.cookies:
        print('Cookies recebidos:', session.cookies.get_dict())
    else:
        print('Nenhum cookie de sessão detectado — verifique se o app está rodando e a rota /login está disponível')


def api_search(session, query):
    url = f"{BASE}/api/search_album"
    print(f'Chamando {url}?q={query}')
    resp = session.get(url, params={'q': query})
    try:
        data = resp.json()
    except Exception:
        print('Resposta não é JSON. Código:', resp.status_code)
        print(resp.text[:1000])
        return
    print('Status:', resp.status_code)
    print('Payload (resumo):')
    if isinstance(data, list):
        for i, it in enumerate(data[:10], start=1):
            print(f"{i}. {it.get('name')} — {it.get('artists')} (id:{it.get('id')})")
    else:
        print(data)


def main():
    query = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'beatles'
    with requests.Session() as s:
        register_if_needed(s)
        time.sleep(0.5)
        login(s)
        time.sleep(0.5)
        api_search(s, query)


if __name__ == '__main__':
    main()
