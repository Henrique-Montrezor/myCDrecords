from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# Importa a instância 'db' do arquivo principal 'app.py'
# Isso funciona porque o 'db' é criado em app.py ANTES
# da inicialização completa.
from app import db 

# --- 2. MODELOS DO BANCO DE DADOS ---
# Estas são as classes que definem a estrutura das tabelas
# do seu banco de dados.

class User(UserMixin, db.Model):
    """ Modelo para a tabela de Usuários """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Define a relação: Um usuário pode ter muitas 'reviews'
    # 'backref' cria um atributo virtual 'author' em cada 'Review'
    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password):
        """ Gera o hash da senha """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Verifica se a senha está correta """
        return check_password_hash(self.password_hash, password)

class Review(db.Model):
    """ Modelo para a tabela de Reviews (Críticas) """
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.String(50), nullable=False) # ID do álbum na API externa
    album_title = db.Column(db.String(200), nullable=False) # Guardamos o título do álbum para referência rápida
    rating = db.Column(db.Integer, nullable=False) # Nota de 1 a 5
    text = db.Column(db.Text, nullable=True)
    
    # Define a chave estrangeira: O 'user_id' desta review aponta para o 'id' da tabela 'user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)