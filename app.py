import os
import requests  # Para chamadas à API externa de álbuns
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from spotify_client import search_albums, get_album

# --- 1. CONFIGURAÇÃO INICIAL ---

# Carrega as variáveis de ambiente (do arquivo .env)
# (Você precisaria instalar 'python-dotenv': pip install python-dotenv)
from dotenv import load_dotenv, find_dotenv
# Tenta localizar o .env a partir do diretório do projeto
DOTENV_PATH = find_dotenv()
if DOTENV_PATH:
    load_dotenv(DOTENV_PATH)
else:
    # fallback: tenta carregar .env padrão (pode não existir)
    load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configurações do App
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_secreta_muito_forte_padrao')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Chave da API externa para buscar álbuns (guardada no arquivo .env)
MUSIC_API_KEY = os.environ.get('MUSIC_API_KEY')
MUSIC_API_URL = os.environ.get('MUSIC_API_URL', 'https://api.themoviedb.org/3')

# Inicializa o Banco de Dados
db = SQLAlchemy(app)

# Inicializa o Gerenciador de Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redireciona para a rota 'login' se não estiver logado
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# --- 2. MODELOS DO BANCO DE DADOS (Exemplo) ---
# (Idealmente, isso estaria em 'models.py', mas para um exemplo simples, pode ficar aqui)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.String(50), nullable=False) # ID do álbum na API externa
    album_title = db.Column(db.String(200), nullable=False) # Guardamos o título do álbum para referência rápida
    rating = db.Column(db.Integer, nullable=False) # Nota de 1 a 5
    text = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Função para carregar um usuário (necessária para o Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 3. ROTAS QUE SERVEM PÁGINAS HTML (Frontend) ---

@app.route('/')
def index():
    """ Página Inicial """
    # Busca as últimas reviews de todos os usuários
    recent_reviews = Review.query.order_by(Review.id.desc()).limit(10).all()
    return render_template('index.html', reviews=recent_reviews)

@app.route('/perfil/<username>')
@login_required
def profile(username):
    """ Página de Perfil de um Usuário """
    user = User.query.filter_by(username=username).first_or_404()
    user_reviews = Review.query.filter_by(user_id=user.id).order_by(Review.id.desc()).all()
    return render_template('profile.html', user=user, reviews=user_reviews)

@app.route('/album/<album_id>')
def album_details(album_id):
    """ Página de Detalhes de um Álbum """
    # 1. Busca dados do álbum na API externa
    album_data = None
    # Se houver uma API externa genérica configurada, tenta buscá-la primeiro
    if MUSIC_API_KEY:
        try:
            resp = requests.get(f"{MUSIC_API_URL}/album/{album_id}", params={
                'api_key': MUSIC_API_KEY,
                'language': 'pt-BR'
            })
            resp.raise_for_status()
            album_data = resp.json()
        except requests.RequestException as e:
            app.logger.error(f"Erro ao buscar álbum {album_id} na API externa: {e}")
            flash('Erro ao carregar detalhes do álbum da API externa; tentando Spotify...', 'warning')
        
    # 2. Busca reviews deste álbum no nosso banco
    album_reviews = Review.query.filter_by(album_id=album_id).all()
    
    # If album_data from external API is not present, try fetching from Spotify
    if not album_data:
        try:
            album_data = get_album(album_id)
        except Exception as e:
            app.logger.error(f"Erro ao buscar álbum na API: {e}")

    return render_template('album_details.html', album=album_data, reviews=album_reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Página de Login """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """ Rota de Logout """
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/registrar', methods=['GET', 'POST'])
def register():
    """ Página de Registro """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Verifica se email ou usuário já existem
        if User.query.filter_by(email=email).first():
            flash('Este email já está em uso.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso.', 'danger')
        else:
            # Cria novo usuário
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html') # Você precisaria criar este template

# --- 4. ROTAS DE API (Backend - Respondem com JSON) ---

@app.route('/api/search_album')
@login_required
def api_search_album():
    """ API para buscar álbuns na API externa """
    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({'error': 'Query não fornecida'}), 400
    try:
        items = search_albums(query, limit=10)
        # Simplify response for the frontend
        results = []
        for it in items:
            artists = ', '.join([a.get('name') for a in it.get('artists', [])])
            img = None
            if it.get('images'):
                img = it['images'][0].get('url')
            results.append({
                'id': it.get('id'),
                'name': it.get('name'),
                'artists': artists,
                'image': img,
                'total_tracks': it.get('total_tracks')
            })
        return jsonify(results)
    except RuntimeError as e:
        # Likely raised by spotify_client when credentials are missing
        app.logger.warning(f"Spotify client runtime error: {e}")
        return jsonify({'error': 'Chave da API não configurada', 'message': str(e)}), 400
    except Exception as e:
        # Log full traceback
        app.logger.exception("Erro ao buscar na API Spotify")
        # If it's an HTTPError from requests, include status and body if available
        err_payload = {'error': 'Falha ao buscar dados externos'}
        try:
            import requests as _req
            if isinstance(e, _req.HTTPError) and getattr(e, 'response', None) is not None:
                resp = e.response
                err_payload['status_code'] = resp.status_code
                # include response body for debugging (safe in dev)
                err_payload['response_text'] = resp.text
        except Exception:
            pass

        # Also include the exception message (helpful in dev)
        err_payload['message'] = str(e)
        return jsonify(err_payload), 502


@app.route('/_debug/env')
def debug_env():
    """Rota de debug para checar presença de variáveis de ambiente (não expõe valores)."""
    return jsonify({
        'SPOTIFY_CLIENT_ID_present': bool(os.environ.get('SPOTIFY_CLIENT_ID')),
        'SPOTIFY_CLIENT_SECRET_present': bool(os.environ.get('SPOTIFY_CLIENT_SECRET')),
        'MUSIC_API_KEY_present': bool(os.environ.get('MUSIC_API_KEY'))
        ,
        'DOTENV_path': DOTENV_PATH or '',
        'cwd': os.getcwd()
    })

@app.route('/api/review/add', methods=['POST'])
@login_required
def api_add_review():
    """ API para adicionar uma nova review """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'JSON inválido ou ausente.'}), 400

    album_id = data.get('album_id')
    title = data.get('album_title')
    rating_value = data.get('rating')
    text = data.get('text', '')

    if not album_id or not title or rating_value is None:
        return jsonify({'status': 'error', 'message': 'Campos obrigatórios ausentes.'}), 400

    try:
        rating = int(rating_value)
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Rating inválido.'}), 400

    if not (1 <= rating <= 5):
        return jsonify({'status': 'error', 'message': 'Rating deve ser entre 1 e 5.'}), 400

    try:
        new_review = Review(
            album_id=album_id,
            album_title=title,
            rating=rating,
            text=text,
            user_id=current_user.id
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Review salva!'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao salvar review: {e}")
        return jsonify({'status': 'error', 'message': 'Erro interno ao salvar review.'}), 500

# --- 5. EXECUÇÃO DA APLICAÇÃO ---

if __name__ == '__main__':
    # Cria as tabelas do banco de dados (se não existirem)
    with app.app_context():
        db.create_all()
        # Verifica se as colunas novas existem e, se não, adiciona-as e popula com valores antigos quando possível.
        try:
            # Pega lista de colunas da tabela 'review'
            res = db.session.execute(text("PRAGMA table_info(review);"))
            cols = [row[1] for row in res.fetchall()]

            # Adiciona coluna 'album_id' se não existir
            if 'album_id' not in cols:
                db.session.execute(text("ALTER TABLE review ADD COLUMN album_id VARCHAR;"))
                if 'tmdb_movie_id' in cols:
                    db.session.execute(text("UPDATE review SET album_id = tmdb_movie_id;"))

            # Adiciona coluna 'album_title' se não existir
            if 'album_title' not in cols:
                db.session.execute(text("ALTER TABLE review ADD COLUMN album_title VARCHAR;"))
                if 'movie_title' in cols:
                    db.session.execute(text("UPDATE review SET album_title = movie_title;"))

            db.session.commit()
        except Exception as e:
            app.logger.error(f"Erro na migração do esquema do DB: {e}")
        
    # Roda o servidor Flask em modo de debug
    # (Não use debug=True em produção!)
    app.run(debug=True, port=5000)