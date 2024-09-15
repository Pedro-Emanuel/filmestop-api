from flask import Blueprint, jsonify, request
from app.models import User, Movie, Rental
from app import db

bp = Blueprint('main', __name__)

@bp.route('/movies/<genre>')
def get_movies_by_genre(genre):
    movies = Movie.query.filter_by(genre=genre).all()
    return jsonify([{'id': m.id, 'title': m.title} for m in movies])

@bp.route('/movies/<int:movie_id>')
def get_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return jsonify({'id': movie.id, 'title': movie.title, 'genre': movie.genre})

@bp.route('/rent', methods=['POST'])
def rent_movie():
    data = request.json
    user = User.query.get_or_404(data['user_id'])
    movie = Movie.query.get_or_404(data['movie_id'])
    rental = Rental(user=user, movie=movie)
    db.session.add(rental)
    db.session.commit()
    return jsonify({'message': 'Movie rented successfully'}), 201

@bp.route('/rate', methods=['POST'])
def rate_movie():
    data = request.json
    rental = Rental.query.filter_by(user_id=data['user_id'], movie_id=data['movie_id']).first_or_404()
    rental.rating = data['rating']
    db.session.commit()
    return jsonify({'message': 'Rating added successfully'})

@bp.route('/user/<int:user_id>/rentals')
def get_user_rentals(user_id):
    rentals = Rental.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'movie_id': r.movie_id,
        'title': r.movie.title,
        'rating': r.rating,
        'rental_date': r.rental_date
    } for r in rentals])