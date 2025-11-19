import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

class Config:
    """
    Classe de configuração principal.
    As variáveis são carregadas do ambiente (arquivo .env)
    e valores padrão são fornecidos por segurança.
    """
    
    # Chave secreta para o Flask (sessões, cookies, etc.)
    # MUITO IMPORTANTE: Mude isso para um valor aleatório em produção
    SECRET_KEY = os.environ.get('SECRET_KEY', 'uma_chave_secreta_muito_forte_padrao')
    
    # URL do Banco de Dados
    # O padrão é um arquivo 'database.db' na raiz do projeto
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Chave da API externa para buscar álbuns (defina no .env se usar uma API)
    MUSIC_API_KEY = os.environ.get('MUSIC_API_KEY')
    MUSIC_API_URL = os.environ.get('MUSIC_API_URL', 'https://api.themoviedb.org/3')
    
    # Configuração opcional do SQLAlchemy para otimização
    SQLALCHEMY_TRACK_MODIFICATIONS = False