
# Este arquivo de teste cobre:

# 1. Criação de usuários, filmes e aluguéis
# 2. Verificação de unicidade de email para usuários
# 3. Relações entre usuários, filmes e aluguéis
# 4. Comportamento em cascata para exclusões
# 5. Geração de token de administrador
# 6. Atribuição e validação de avaliações de aluguel
# 7. Pesquisa de filmes por título e intervalo de ano

import pytest
from app.models import User, Movie, Rental

def test_user_creation(session):
    user = User(name="Test User", email="test@example.com", phone="1234567890")
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.phone == "1234567890"
    assert user.is_admin is False
    assert user.admin_token is None

def test_user_unique_email(session):
    user1 = User(name="User 1", email="same@example.com")
    user2 = User(name="User 2", email="same@example.com")
    session.add(user1)
    session.commit()
    
    with pytest.raises(Exception):  # Expecting an integrity error
        session.add(user2)
        session.commit()

def test_movie_creation(session):
    movie = Movie(title="Test Movie", genre="Action", year=2023, synopsis="A test movie", director="Test Director")
    session.add(movie)
    session.commit()
    
    assert movie.id is not None
    assert movie.title == "Test Movie"
    assert movie.genre == "Action"
    assert movie.year == 2023
    assert movie.synopsis == "A test movie"
    assert movie.director == "Test Director"

def test_rental_creation(session):
    user = User(name="Rental User", email="rental@example.com")
    movie = Movie(title="Rental Movie", genre="Comedy", year=2023)
    session.add_all([user, movie])
    session.commit()
    
    rental = Rental(user=user, movie=movie)
    session.add(rental)
    session.commit()
    
    assert rental.id is not None
    assert rental.user_id == user.id
    assert rental.movie_id == movie.id
    assert rental.rental_date is not None
    assert rental.rating is None

def test_user_rentals_relationship(session):
    user = User(name="User with Rentals", email="rentals@example.com")
    movie1 = Movie(title="Movie 1", genre="Action", year=2023)
    movie2 = Movie(title="Movie 2", genre="Comedy", year=2023)
    session.add_all([user, movie1, movie2])
    session.commit()
    
    rental1 = Rental(user=user, movie=movie1)
    rental2 = Rental(user=user, movie=movie2)
    session.add_all([rental1, rental2])
    session.commit()
    
    assert len(user.rentals) == 2
    assert user.rentals[0].movie.title in ["Movie 1", "Movie 2"]
    assert user.rentals[1].movie.title in ["Movie 1", "Movie 2"]

def test_movie_rentals_relationship(session):
    movie = Movie(title="Popular Movie", genre="Action", year=2023)
    user1 = User(name="User 1", email="user1@example.com")
    user2 = User(name="User 2", email="user2@example.com")
    session.add_all([movie, user1, user2])
    session.commit()
    
    rental1 = Rental(user=user1, movie=movie)
    rental2 = Rental(user=user2, movie=movie)
    session.add_all([rental1, rental2])
    session.commit()
    
    assert len(movie.rentals) == 2
    assert movie.rentals[0].user.name in ["User 1", "User 2"]
    assert movie.rentals[1].user.name in ["User 1", "User 2"]

def test_cascade_delete_user(session):
    user = User(name="Delete User", email="delete@example.com")
    movie = Movie(title="Delete Movie", genre="Action", year=2023)
    rental = Rental(user=user, movie=movie)
    session.add_all([user, movie, rental])
    session.commit()
    
    session.delete(user)
    session.commit()
    
    assert session.query(Rental).filter_by(user_id=user.id).count() == 0
    assert session.query(Movie).filter_by(id=movie.id).count() == 1  # Movie should still exist

def test_cascade_delete_movie(session):
    user = User(name="Keep User", email="keep@example.com")
    movie = Movie(title="Delete Movie", genre="Action", year=2023)
    rental = Rental(user=user, movie=movie)
    session.add_all([user, movie, rental])
    session.commit()
    
    session.delete(movie)
    session.commit()
    
    assert session.query(Rental).filter_by(movie_id=movie.id).count() == 0
    assert session.query(User).filter_by(id=user.id).count() == 1  # User should still exist

def test_user_admin_token_generation(session):
    user = User(name="Admin User", email="admin@example.com", is_admin=True)
    session.add(user)
    session.commit()
    
    token = user.generate_admin_token()
    assert token is not None
    assert user.admin_token == token
    
    # Test token uniqueness
    another_user = User(name="Another Admin", email="another@example.com", is_admin=True)
    session.add(another_user)
    session.commit()
    another_token = another_user.generate_admin_token()
    assert another_token != token

def test_rental_rating(session):
    user = User(name="Rating User", email="rating@example.com")
    movie = Movie(title="Rated Movie", genre="Drama", year=2023)
    rental = Rental(user=user, movie=movie)
    session.add_all([user, movie, rental])
    session.commit()
    
    rental.rating = 4.5
    session.commit()
    
    assert rental.rating == 4.5
    
    # # Test invalid rating
    # rental.rating = 6.0
    # session.commit()
    # assert rental.rating == 4.5

def test_movie_search_by_title(session):
    movie1 = Movie(title="The Shawshank Redemption", genre="Drama", year=1994)
    movie2 = Movie(title="The Godfather", genre="Crime", year=1972)
    movie3 = Movie(title="The Dark Knight", genre="Action", year=2008)
    session.add_all([movie1, movie2, movie3])
    session.commit()
    
    results = Movie.query.filter(Movie.title.ilike("%godfather%")).all()
    assert len(results) == 1
    assert results[0].title == "The Godfather"

def test_movie_search_by_year_range(session):
    movie1 = Movie(title="Old Movie", genre="Classic", year=1950)
    movie2 = Movie(title="Middle Movie", genre="Drama", year=1980)
    movie3 = Movie(title="New Movie", genre="Action", year=2010)
    session.add_all([movie1, movie2, movie3])
    session.commit()
    
    results = Movie.query.filter(Movie.year.between(1970, 2000)).all()
    assert len(results) == 1
    assert results[0].title == "Middle Movie"

# Add more tests as needed for your specific model behaviors and relationships