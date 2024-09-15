# Este conjunto de testes cobre:

# 1. Todos os endpoints principais da API
# 2. Casos de sucesso e erro para cada endpoint
# 3. Validação de entrada
# 4. Paginação
# 5. Pesquisa parcial
# 6. Codificação UTF-8
# 7. Consistência de dados após operações
# 8. Limites de avaliação

# Alguns pontos importantes:

# - O fixture `client` cria um cliente de teste e configura um banco de dados de teste em memória.
# - O fixture `init_database` popula o banco de dados com dados de teste.
# - Cada teste verifica não apenas o status code da resposta, mas também o conteúdo retornado.
# - Há testes para cenários de erro, como usuários ou filmes inválidos.
# - O teste de codificação UTF-8 garante que caracteres especiais sejam tratados corretamente.
# - O teste de paginação verifica se a API lida corretamente com conjuntos maiores de dados.
# - Há testes de validação de entrada para garantir que a API rejeite dados inválidos.
# - O teste de consistência de dados verifica se os aluguéis são registrados corretamente no banco de dados.

import json
import pytest
from app import db
from app.models import User, Movie, Rental
from datetime import datetime, timedelta

# Testes para GET /movies
def test_movies(client, init_database):
    response = client.get('/movies')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['titulo'] == "Test Movie 1"
    assert data[1]['titulo'] == "Test Movie 2"

# Testes para GET /movies/genre
def test_get_movies_by_genre(client, init_database):
    response = client.get('/movies/genre?genre=Action')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['filmes']) == 1
    assert data['filmes'][0]['titulo'] == "Test Movie 1"

def test_get_movies_by_genre_not_found(client, init_database):
    response = client.get('/movies/genre?genre=Horror')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "Nenhum filme encontrado" in data['mensagem']

def test_get_movies_by_genre_no_genre_provided(client, init_database):
    response = client.get('/movies/genre')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "O parâmetro 'genre' é obrigatório" in data['erro']

# Testes para GET /movies/<id>
def test_get_movie_details(client, init_database):
    movie_id = init_database['movies'][0].id
    response = client.get(f'/movies/{movie_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['titulo'] == "Test Movie 1"
    assert data['genero'] == "Action"

def test_get_movie_details_not_found(client, init_database):
    response = client.get('/movies/999')
    assert response.status_code == 404

# Testes para POST /rent
def test_rent_movie(client, init_database):
    user_id = init_database['users'][0].id
    movie_id = init_database['movies'][0].id
    response = client.post('/rent', 
                           json={'user_id': user_id, 'movie_id': movie_id},
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "Filme alugado com sucesso" in data['mensagem']

def test_rent_movie_invalid_user(client, init_database):
    movie_id = init_database['movies'][0].id
    response = client.post('/rent', 
                           json={'user_id': 999, 'movie_id': movie_id},
                           content_type='application/json')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "Usuário ou Filme não encontrado" in data['erro']

def test_rent_movie_invalid_movie(client, init_database):
    user_id = init_database['users'][0].id
    response = client.post('/rent', 
                           json={'user_id': user_id, 'movie_id': 999},
                           content_type='application/json')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "Usuário ou Filme não encontrado" in data['erro']

# Testes para POST /rate
def test_rate_movie(client, init_database):
    user_id = init_database['users'][0].id
    movie_id = init_database['movies'][0].id
    # Primeiro, alugar o filme
    client.post('/rent', 
                json={'user_id': user_id, 'movie_id': movie_id},
                content_type='application/json')
    # Agora, avaliar o filme
    response = client.post('/rate', 
                           json={'user_id': user_id, 'movie_id': movie_id, 'rating': 4.5},
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "Filme avaliado com sucesso" in data['mensagem']

def test_rate_movie_not_rented(client, init_database):
    user_id = init_database['users'][0].id
    movie_id = init_database['movies'][0].id
    response = client.post('/rate', 
                           json={'user_id': user_id, 'movie_id': movie_id, 'rating': 4.5},
                           content_type='application/json')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "Aluguel não encontrado" in data['erro']

def test_rate_movie_invalid_rating(client, init_database):
    user_id = init_database['users'][0].id
    movie_id = init_database['movies'][0].id
    client.post('/rent', 
                json={'user_id': user_id, 'movie_id': movie_id},
                content_type='application/json')
    response = client.post('/rate', 
                           json={'user_id': user_id, 'movie_id': movie_id, 'rating': 6},
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Erro de validação" in data['erro']

# Testes para GET /users/<id>/rentals
def test_get_user_rentals(client, init_database):
    user_id = init_database['users'][0].id
    movie_id = init_database['movies'][0].id
    # Alugar um filme
    client.post('/rent', 
                json={'user_id': user_id, 'movie_id': movie_id},
                content_type='application/json')
    # Obter aluguéis do usuário
    response = client.get(f'/users/{user_id}/rentals')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['titulo_filme'] == "Test Movie 1"

def test_get_user_rentals_no_rentals(client, init_database):
    user_id = init_database['users'][0].id
    response = client.get(f'/users/{user_id}/rentals')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0

def test_get_user_rentals_invalid_user(client, init_database):
    response = client.get('/users/999/rentals')
    assert response.status_code == 404

# Teste para verificar a codificação UTF-8
def test_utf8_encoding(client, init_database):
    movie = Movie(title="Filme com Acentuação", genre="Comédia", year=2023, synopsis="Sinopse com caracteres especiais: áéíóú", director="Diretor")
    db.session.add(movie)
    db.session.commit()

    response = client.get(f'/movies/{movie.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['titulo'] == "Filme com Acentuação"
    assert data['genero'] == "Comédia"
    assert "áéíóú" in data['sinopse']

# Teste de paginação
def test_movies_pagination(client, init_database):
    # Adicionar mais filmes para testar a paginação
    for i in range(22):
        movie = Movie(title=f"Pagination Movie {i}", genre="Test", year=2023)
        db.session.add(movie)
    db.session.commit()

    response = client.get('/movies/genre?genre=Test&page=2&per_page=10')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['filmes']) == 10
    assert data['pagina_atual'] == 2
    assert data['total_filmes'] == 22
    assert data['total_paginas'] == 3  # 22 filmes no total, 10 por página

# Teste de pesquisa parcial de gênero
def test_partial_genre_search(client, init_database):
    response = client.get('/movies/genre?genre=com')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['filmes']) == 1
    assert data['filmes'][0]['genero'] == "Comedy"

# Teste de validação de entrada
def test_input_validation(client, init_database):
    user_id = init_database['users'][0].id
    response = client.post('/rent', 
                           json={'user_id': user_id, 'movie_id': 'not_a_number'},
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Erro de validação" in data['erro']

# Teste de consistência de dados após aluguel
def test_rental_data_consistency(client, init_database):
    user_id = init_database['users'][0].id
    movie_id = init_database['movies'][0].id
    client.post('/rent', 
                json={'user_id': user_id, 'movie_id': movie_id},
                content_type='application/json')
    
    with client.application.app_context():
        rental = Rental.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        assert rental is not None
        assert rental.user_id == user_id
        assert rental.movie_id == movie_id
        assert (datetime.utcnow() - rental.rental_date).total_seconds() < 60  # Aluguel feito há menos de 1 minuto

# Teste de limite de avaliação
def test_rating_limit(client, init_database):
    user_id = init_database['users'][0].id
    movie_id = init_database['movies'][0].id
    client.post('/rent', 
                json={'user_id': user_id, 'movie_id': movie_id},
                content_type='application/json')
    
    response = client.post('/rate', 
                           json={'user_id': user_id, 'movie_id': movie_id, 'rating': 5.1},
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Erro de validação" in data['erro']

    response = client.post('/rate', 
                           json={'user_id': user_id, 'movie_id': movie_id, 'rating': -0.1},
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Erro de validação" in data['erro']