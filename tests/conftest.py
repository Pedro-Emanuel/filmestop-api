import pytest
from app import create_app, db
from app.models import User, Movie, Rental
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    return app

@pytest.fixture(scope='session')
def _db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(_db, app):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection, binds={})
        session_factory = sessionmaker(**options)
        session = scoped_session(session_factory)
        
        _db.session = session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(session):
    # Criar usuários de teste
    user1 = User(name="Test User 1", email="user1@test.com")
    user2 = User(name="Test User 2", email="user2@test.com")
    
    # Criar filmes de teste
    movie1 = Movie(title="Test Movie 1", genre="Action", year=2021, synopsis="Test synopsis 1", director="Test Director 1")
    movie2 = Movie(title="Test Movie 2", genre="Comedy", year=2022, synopsis="Test synopsis 2", director="Test Director 2")
    
    session.add_all([user1, user2, movie1, movie2])
    session.commit()

    return {"users": [user1, user2], "movies": [movie1, movie2]}