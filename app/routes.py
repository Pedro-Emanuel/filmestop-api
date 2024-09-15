# -*- coding: utf-8 -*-

from flask import Blueprint, abort, jsonify, request
from app import db
from app.models import User, Movie, Rental
from marshmallow import Schema, fields, validate, ValidationError
from http import HTTPStatus
from functools import wraps
from sqlalchemy import func, text
from urllib.parse import unquote

bp = Blueprint('main', __name__)

# Mensagens de erro em português
ERRO_VALIDACAO = "Erro de validação dos dados de entrada"
ERRO_INTERNO = "Ocorreu um erro interno no servidor"
ERRO_NAO_ENCONTRADO = "Recurso não encontrado"

# Esquemas de validação de entrada
class RentMovieSchema(Schema):
    user_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do usuário é obrigatório', 'invalid': 'O ID do usuário deve ser um número inteiro positivo'})
    movie_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do filme é obrigatório', 'invalid': 'O ID do filme deve ser um número inteiro positivo'})

class RateMovieSchema(Schema):
    user_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do usuário é obrigatório', 'invalid': 'O ID do usuário deve ser um número inteiro positivo'})
    movie_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do filme é obrigatório', 'invalid': 'O ID do filme deve ser um número inteiro positivo'})
    rating = fields.Float(required=True, validate=validate.Range(min=0, max=5), error_messages={'required': 'A avaliação é obrigatória', 'invalid': 'A avaliação deve ser um número entre 0 e 5'})

# Manipulador de erros global para o blueprint
@bp.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"erro": ERRO_VALIDACAO, "detalhes": error.messages}), HTTPStatus.BAD_REQUEST

@bp.errorhandler(Exception)
def handle_generic_error(error):
    return jsonify({"erro": ERRO_INTERNO, "detalhes": str(error)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.errorhandler(404)
def handle_not_found(error):
    return jsonify({"erro": ERRO_NAO_ENCONTRADO}), HTTPStatus.NOT_FOUND

# Rota raiz
@bp.route('/')
def index():
    return jsonify({'mensagem': 'API de locadora de filmes'}), HTTPStatus.OK

# Rota para alugar um filme
@bp.route('/rent', methods=['POST'])
def rent_movie():
    data = RentMovieSchema().load(request.json)
    user = db.session.get(User, data['user_id'])
    movie = db.session.get(Movie, data['movie_id'])
    
    if not user or not movie:
        return jsonify({'erro': 'Usuário ou Filme não encontrado'}), HTTPStatus.NOT_FOUND
    
    rental = Rental(user=user, movie=movie)
    db.session.add(rental)
    db.session.commit()
    
    return jsonify({'mensagem': 'Filme alugado com sucesso'}), HTTPStatus.CREATED

# Rota para avaliar um filme
@bp.route('/rate', methods=['POST'])
def rate_movie():
    data = RateMovieSchema().load(request.json)
    rental = Rental.query.filter_by(user_id=data['user_id'], movie_id=data['movie_id']) \
                         .order_by(Rental.rental_date.desc()).first()
    
    if not rental:
        return jsonify({'erro': 'Aluguel não encontrado'}), HTTPStatus.NOT_FOUND
    
    rental.rating = data['rating']
    db.session.commit()
    
    return jsonify({'mensagem': 'Filme avaliado com sucesso'}), HTTPStatus.OK

# Rota para listar todos os filmes
@bp.route('/movies')
def list_movies():
    movies = Movie.query.all()
    return jsonify([
        {
            'id': m.id,
            'titulo': m.title,
            'genero': m.genre,
            'ano': m.year
        } for m in movies
    ]), HTTPStatus.OK
    
# Rota para listar filmes por gênero (com paginação, case insensitive e busca parcial)
@bp.route('/movies/genre')
def get_movies_by_genre():
    genre = unquote(request.args.get('genre', '').strip())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not genre:
        return jsonify({"erro": "O parâmetro 'genre' é obrigatório"}), HTTPStatus.BAD_REQUEST

    movies = Movie.query.filter(func.lower(Movie.genre).like(f"%{genre.lower()}%")) \
                        .paginate(page=page, per_page=per_page, error_out=False)

    if not movies.items:
        return jsonify({"mensagem": f"Nenhum filme encontrado para o gênero '{genre}'"}), HTTPStatus.NOT_FOUND
    
    return jsonify({
        'filmes': [
            {
                'id': m.id,
                'titulo': m.title,
                'genero': m.genre,
                'ano': m.year,
                'diretor': m.director
            } for m in movies.items
        ],
        'pagina_atual': movies.page,
        'total_paginas': movies.pages,
        'total_filmes': movies.total
    }), HTTPStatus.OK

# Rota para obter detalhes de um filme específico
@bp.route('/movies/<int:movie_id>')
def get_movie_details(movie_id):
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        abort(HTTPStatus.NOT_FOUND)
    return jsonify({
        'id': movie.id,
        'titulo': movie.title,
        'genero': movie.genre,
        'ano': movie.year,
        'sinopse': movie.synopsis,
        'diretor': movie.director
    }), HTTPStatus.OK

# Rota para listar todos os aluguéis de um usuário específico
@bp.route('/users/<int:user_id>/rentals')
def list_user_rentals(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(HTTPStatus.NOT_FOUND)
    rentals = Rental.query.filter_by(user_id=user_id).order_by(Rental.rental_date.desc()).all()
    return jsonify([
        {
            'id': r.id,
            'titulo_filme': r.movie.title,
            'data_aluguel': r.rental_date.isoformat(),
            'avaliacao': r.rating
        } for r in rentals
    ]), HTTPStatus.OK

@bp.route('/test_db')
def test_db():
    try:
        result = db.session.execute(text("SELECT 1"))
        return jsonify({'message': 'Conexão com o banco de dados bem-sucedida!', 'result': result.scalar()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin Required

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"erro": "Token de autenticação não fornecido"}), HTTPStatus.UNAUTHORIZED
        
        user = User.query.filter_by(admin_token=token).first()
        if not user or not user.is_admin:
            return jsonify({"erro": "Acesso não autorizado"}), HTTPStatus.FORBIDDEN
        
        return f(*args, **kwargs)
    return decorated_function

def add_user(name, email, phone):
    user = User(name=name, email=email, phone=phone)
    db.session.add(user)
    db.session.commit()
    return user

def add_movie(title, genre, year, synopsis, director):
    movie = Movie(title=title, genre=genre, year=year, synopsis=synopsis, director=director)
    db.session.add(movie)
    db.session.commit()
    return movie

def clear_database():
    Rental.query.delete()
    Movie.query.delete()
    User.query.delete()
    db.session.commit()
    
@bp.route('/add_user', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    user = add_user(data['name'], data['email'], data.get('phone'))
    return jsonify({'message': 'Usuário adicionado com sucesso', 'id': user.id}), HTTPStatus.CREATED

@bp.route('/add_movie', methods=['POST'])
@admin_required
def create_movie():
    data = request.json
    movie = add_movie(data['title'], data['genre'], data['year'], data.get('synopsis'), data.get('director'))
    return jsonify({'message': 'Filme adicionado com sucesso', 'id': movie.id}), HTTPStatus.CREATED

@bp.route('/clear_database', methods=['POST'])
@admin_required
def clear_db():
    clear_database()
    return jsonify({'message': 'Banco de dados limpo com sucesso'}), HTTPStatus.OK

@bp.route('/populate_database', methods=['POST'])
@admin_required
def populate_db():
    clear_database()
    
    # Adicionar usuários
    users = [
        ("João Silva", "joao@email.com", "123456789"),
        ("Maria Oliveira", "maria@email.com", "987654321"),
        ("José Santos", "jose@email.com", "456789123"),
        ("Ana Souza", "ana@email.com", "654321987"),
        ("Carlos Pereira", "carlos@email.com", "321654987"),
        ("Lucas Almeida", "lucas@email.com", "159753486"),
        ("Fernanda Lima", "fernanda@email.com", "357951468"),
        ("Gabriel Costa", "gabriel@email.com", "741258963"),
        ("Juliana Rocha", "juliana@email.com", "852963741"),
        ("Roberto Mendes", "roberto@email.com", "963852741"),
        ("Patricia Martins", "patricia@email.com", "147258369"),
        ("Thiago Oliveira", "thiago@email.com", "258963147"),
        ("Julio Cesar", "julio@email.com", "369147258"),
        ("Vanessa Pereira", "vanessa@email.com", "741369852"),
        ("Ricardo Santos", "ricardo@email.com", "852741963"),
        ("Camila Barbosa", "camila@email.com", "963741258"),
        ("Eduardo Lima", "eduardo@email.com", "258147963"),
        ("Larissa Silva", "larissa@email.com", "147963258"),
        ("Marcos Paulo", "marcos@email.com", "369258147"),
        ("Gabriela Souza", "gabriela@email.com", "741852963")
    ]
    
    for name, email, phone in users:
        add_user(name, email, phone)
    
    # Adicionar filmes
    movies = [
        ("O Poderoso Chefão", "Drama", 1972, "A história da família Corleone", "Francis Ford Coppola"),
        ("Matrix", "Ficção Científica", 1999, "Um hacker descobre a verdade sobre sua realidade", "Lana e Lilly Wachowski"),
        ("Titanic", "Romance", 1997, "O amor impossível entre Jack e Rose", "James Cameron"),
        ("Os Caça-Fantasmas", "Comédia", 1984, "Uma equipe de caça-fantasmas salva Nova York de fantasmas", "Ivan Reitman"),
        ("Pulp Fiction", "Crime", 1994, "Várias histórias se entrelaçam em Los Angeles", "Quentin Tarantino"),
        ("O Senhor dos Anéis: A Sociedade do Anel", "Fantasia", 2001, "A jornada para destruir o Anel do Poder", "Peter Jackson"),
        ("Star Wars: Episódio IV - Uma Nova Esperança", "Aventura", 1977, "A luta contra o Império Galáctico", "George Lucas"),
        ("O Silêncio dos Inocentes", "Suspense", 1991, "A caçada a um serial killer com a ajuda de um psicopata encarcerado", "Jonathan Demme"),
        ("Clube da Luta", "Drama", 1999, "Um homem desencadeia uma revolução interna com um clube secreto", "David Fincher"),
        ("Gladiador", "Ação", 2000, "Um general romano busca vingança contra o imperador que matou sua família", "Ridley Scott"),
        ("A Origem", "Ficção Científica", 2010, "Um ladrão especializado em extrair segredos do subconsciente", "Christopher Nolan"),
        ("Forrest Gump", "Drama", 1994, "A vida extraordinária de um homem com QI baixo", "Robert Zemeckis"),
        ("O Grande Lebowski", "Comédia", 1998, "Um homem é confundido com um milionário e se envolve em uma trama complicada", "Joel e Ethan Coen"),
        ("Avatar", "Ficção Científica", 2009, "Um ex-fuzileiro naval se torna um avatar em um planeta alienígena", "James Cameron"),
        ("Cidadão Kane", "Drama", 1941, "A vida do magnata de mídia Charles Foster Kane", "Orson Welles"),
        ("Casablanca", "Romance", 1942, "Um café em Casablanca durante a Segunda Guerra Mundial", "Michael Curtiz"),
        ("O Exorcista", "Terror", 1973, "A luta contra a possessão demoníaca de uma jovem", "William Friedkin"),
        ("O Labirinto do Fauno", "Fantasia", 2006, "Uma menina encontra um mundo mágico durante a Guerra Civil Espanhola", "Guillermo del Toro"),
        ("O Rei Leão", "Animação", 1994, "A história de um jovem leão que deve reclamar seu reino", "Roger Allers e Rob Minkoff"),
        ("O Poderoso Chefão II", "Drama", 1974, "Continuação da saga da família Corleone", "Francis Ford Coppola")
    ]
    
    for title, genre, year, synopsis, director in movies:
        add_movie(title, genre, year, synopsis, director)
    
    return jsonify({'message': 'Banco de dados populado com dados de exemplo'}), HTTPStatus.OK

@bp.route('/create_admin', methods=['POST'])
def create_admin():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user:
        if user.is_admin:
            return jsonify({"message": "Usuário já é um administrador"}), HTTPStatus.BAD_REQUEST
        user.is_admin = True
    else:
        user = User(name=data['name'], email=data['email'], phone=data.get('phone'), is_admin=True)
        db.session.add(user)
    
    token = user.generate_admin_token()
    db.session.commit()
    
    return jsonify({"message": "Administrador criado com sucesso", "admin_token": token}), HTTPStatus.CREATED