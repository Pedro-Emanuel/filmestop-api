from flask import Blueprint, abort, request
from app.models import User, Movie, Rental
from app.schemas import RentMovieSchema, RateMovieSchema
from app.utils import ResponseFactory, DatabaseRepository, DatabaseManager
from marshmallow import ValidationError
from http import HTTPStatus
from functools import wraps
from sqlalchemy import func, text
from urllib.parse import unquote

bp = Blueprint('main', __name__)

# Mensagens de erro em português
ERRO_VALIDACAO = "Erro de validação dos dados de entrada"
ERRO_INTERNO = "Ocorreu um erro interno no servidor"
ERRO_NAO_ENCONTRADO = "Recurso não encontrado"

# Manipulador de erros global para o blueprint
@bp.errorhandler(ValidationError)
def handle_validation_error(error):
    return ResponseFactory.create_response({"erro": ERRO_VALIDACAO, "detalhes": error.messages}, HTTPStatus.BAD_REQUEST)

@bp.errorhandler(Exception)
def handle_generic_error(error):
    return ResponseFactory.create_response({"erro": ERRO_INTERNO, "detalhes": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)

@bp.errorhandler(404)
def handle_not_found(error):
    return ResponseFactory.create_response({"erro": ERRO_NAO_ENCONTRADO}, HTTPStatus.NOT_FOUND)

# Decorador para autenticação de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return ResponseFactory.create_response({"erro": "Token de autenticação não fornecido"}, HTTPStatus.UNAUTHORIZED)
        
        user = User.query.filter_by(admin_token=token).first()
        if not user or not user.is_admin:
            return ResponseFactory.create_response({"erro": "Acesso não autorizado"}, HTTPStatus.FORBIDDEN)
        
        return f(*args, **kwargs)
    return decorated_function

# Rotas

@bp.route('/')
def index():
    """
    Rota raiz da API.
    """
    return ResponseFactory.create_response({'mensagem': 'API de locadora de filmes (aprenda como usar em github.com/Pedro-Emanuel/filmestop-api)'}, HTTPStatus.OK)

@bp.route('/rent', methods=['POST'])
def rent_movie():
    """
    Rota para alugar um filme.
    """
    data = RentMovieSchema().load(request.json)
    user = DatabaseRepository.get_by_id(User, data['user_id'])
    movie = DatabaseRepository.get_by_id(Movie, data['movie_id'])
    
    if not user or not movie:
        return ResponseFactory.create_response({'erro': 'Usuário ou Filme não encontrado'}, HTTPStatus.NOT_FOUND)
    
    rental = Rental(user=user, movie=movie)
    DatabaseRepository.add(rental)
    
    return ResponseFactory.create_response({'mensagem': 'Filme alugado com sucesso'}, HTTPStatus.CREATED)

@bp.route('/rate', methods=['POST'])
def rate_movie():
    """
    Rota para avaliar um filme alugado.
    """
    data = RateMovieSchema().load(request.json)
    rental = Rental.query.filter_by(user_id=data['user_id'], movie_id=data['movie_id']) \
                         .order_by(Rental.rental_date.desc()).first()
    
    if not rental:
        return ResponseFactory.create_response({'erro': 'Aluguel não encontrado'}, HTTPStatus.NOT_FOUND)
    
    rental.rating = data['rating']
    db_session = DatabaseManager().get_session()
    db_session.commit()
    
    movie = DatabaseRepository.get_by_id(Movie, data['movie_id'])
    if not movie:
        return ResponseFactory.create_response({'erro': 'Filme não encontrado'}, HTTPStatus.NOT_FOUND)
    
    total_ratings = Rental.query.filter_by(movie_id=data['movie_id']).count()
    average_rating = Rental.query.filter_by(movie_id=data['movie_id']).with_entities(func.avg(Rental.rating)).scalar()
    
    movie.total_ratings = total_ratings
    movie.final_grade = average_rating
    db_session.commit()
    
    return ResponseFactory.create_response({
        'mensagem': 'Filme avaliado com sucesso',
        'total_ratings': total_ratings,
        'final_grade': average_rating
    }, HTTPStatus.OK)

@bp.route('/movies')
def list_movies():
    """
    Rota para listar todos os filmes.
    """
    movies = Movie.query.all()
    return ResponseFactory.create_response([
        {
            'id': m.id,
            'titulo': m.title,
            'genero': m.genre,
            'ano': m.year
        } for m in movies
    ], HTTPStatus.OK)
    
@bp.route('/movies/genre')
def get_movies_by_genre():
    """
    Rota para listar filmes por gênero.
    """
    genre = unquote(request.args.get('genre', '').strip())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not genre:
        return ResponseFactory.create_response({"erro": "O parâmetro 'genre' é obrigatório"}, HTTPStatus.BAD_REQUEST)

    movies = Movie.query.filter(func.lower(Movie.genre).like(f"%{genre.lower()}%")) \
                        .paginate(page=page, per_page=per_page, error_out=False)

    if not movies.items:
        return ResponseFactory.create_response({"mensagem": f"Nenhum filme encontrado para o gênero '{genre}'"}, HTTPStatus.NOT_FOUND)
    
    return ResponseFactory.create_response({
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
    }, HTTPStatus.OK)

@bp.route('/movies/<int:movie_id>')
def get_movie_details(movie_id):
    """
    Rota para obter detalhes de um filme específico.
    """
    movie = DatabaseRepository.get_by_id(Movie, movie_id)
    if movie is None:
        abort(HTTPStatus.NOT_FOUND)
    return ResponseFactory.create_response({
        'id': movie.id,
        'titulo': movie.title,
        'genero': movie.genre,
        'ano': movie.year,
        'sinopse': movie.synopsis,
        'diretor': movie.director,
        'nota_final': movie.final_grade,
        'total_avaliacoes': movie.total_ratings
    }, HTTPStatus.OK)

@bp.route('/users/<int:user_id>/rentals')
def list_user_rentals(user_id):
    """
    Rota para listar todos os aluguéis de um usuário específico.
    """
    user = DatabaseRepository.get_by_id(User, user_id)
    if user is None:
        abort(HTTPStatus.NOT_FOUND)
    rentals = Rental.query.filter_by(user_id=user_id).order_by(Rental.rental_date.desc()).all()
    return ResponseFactory.create_response([
        {
            'id': r.id,
            'titulo_filme': r.movie.title,
            'data_aluguel': r.rental_date.isoformat(),
            'avaliacao': r.rating
        } for r in rentals
    ], HTTPStatus.OK)

@bp.route('/test_db')
def test_db():
    """
    Rota para testar a conexão com o banco de dados.
    """
    try:
        result = DatabaseManager().get_session().execute(text("SELECT 1"))
        return ResponseFactory.create_response({'message': 'Conexão com o banco de dados bem-sucedida!', 'result': result.scalar()}, 200)
    except Exception as e:
        return ResponseFactory.create_response({'error': str(e)}, 500)
    
@bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """
    Rota para listar todos os usuários (apenas para admins).
    """
    users = User.query.all()
    return ResponseFactory.create_response([
        {
            'id': u.id,
            'nome': u.name,
            'email': u.email,
            'telefone': u.phone
        } for u in users
    ], HTTPStatus.OK)    

@bp.route('/add_user', methods=['POST'])
@admin_required
def create_user():
    """
    Rota para adicionar um novo usuário (apenas para admins).
    
    Espera um JSON com name, email e opcionalmente phone.
    
    Retorna:
        Uma mensagem de sucesso com o ID do usuário criado.
    """
    data = request.json
    user = User(name=data['name'], email=data['email'], phone=data.get('phone'))
    DatabaseRepository.add(user)
    return ResponseFactory.create_response({'message': 'Usuário adicionado com sucesso', 'id': user.id}, HTTPStatus.CREATED)

@bp.route('/add_movie', methods=['POST'])
@admin_required
def create_movie():
    """
    Rota para adicionar um novo filme (apenas para admins).
    
    Espera um JSON com title, genre, year e opcionalmente synopsis e director.
    
    Retorna:
        Uma mensagem de sucesso com o ID do filme criado.
    """
    data = request.json
    movie = Movie(title=data['title'], genre=data['genre'], year=data['year'], synopsis=data.get('synopsis'), director=data.get('director'))
    DatabaseRepository.add(movie)
    return ResponseFactory.create_response({'message': 'Filme adicionado com sucesso', 'id': movie.id}, HTTPStatus.CREATED)

@bp.route('/clear_database', methods=['POST'])
@admin_required
def clear_db():
    """
    Rota para limpar o banco de dados (apenas para admins).
    
    Remove todos os registros de Rental, Movie e User.
    
    Retorna:
        Uma mensagem indicando o sucesso da operação.
    """
    DatabaseRepository.delete_all()
    return ResponseFactory.create_response({'message': 'Banco de dados limpo com sucesso'}, HTTPStatus.OK)

@bp.route('/populate_database', methods=['POST'])
@admin_required
def populate_db():
    """
    Rota para popular o banco de dados com dados de exemplo (apenas para admins).
    
    Limpa o banco de dados existente e adiciona usuários e filmes de exemplo.
    
    Retorna:
        Uma mensagem indicando o sucesso da operação.
    """
    DatabaseRepository.delete_all()
    
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
        DatabaseRepository.add(User(name=name, email=email, phone=phone))
    
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
        DatabaseRepository.add(Movie(title=title, genre=genre, year=year, synopsis=synopsis, director=director))
        
    return ResponseFactory.create_response({'message': 'Banco de dados populado com sucesso'}, HTTPStatus.OK)

@bp.route('/create_admin', methods=['POST'])
def create_admin():
    """
    Rota para criar um novo administrador.
    
    Espera um JSON com name, email e opcionalmente phone.
    Cria um novo usuário com privilégios de administrador e gera um token de admin.
    
    Retorna:
        Uma mensagem de sucesso com o token de admin gerado.
    """
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user:
        if user.is_admin:
            return ResponseFactory.create_response({"message": "Usuário já é um administrador"}, HTTPStatus.BAD_REQUEST)
        user.is_admin = True
    else:
        user = User(name=data['name'], email=data['email'], phone=data.get('phone'), is_admin=True)
        DatabaseRepository.add(user)
    
    token = user.generate_admin_token()
    DatabaseManager().get_session().commit()
    
    return ResponseFactory.create_response({"message": "Administrador criado com sucesso", "admin_token": token}, HTTPStatus.CREATED)