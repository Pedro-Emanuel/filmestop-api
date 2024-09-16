from marshmallow import Schema, fields, validate

class RentMovieSchema(Schema):
    user_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do usuário é obrigatório', 'invalid': 'O ID do usuário deve ser um número inteiro positivo'})
    movie_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do filme é obrigatório', 'invalid': 'O ID do filme deve ser um número inteiro positivo'})

class RateMovieSchema(Schema):
    user_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do usuário é obrigatório', 'invalid': 'O ID do usuário deve ser um número inteiro positivo'})
    movie_id = fields.Int(required=True, validate=validate.Range(min=1), error_messages={'required': 'O ID do filme é obrigatório', 'invalid': 'O ID do filme deve ser um número inteiro positivo'})
    rating = fields.Float(required=True, validate=validate.Range(min=0, max=5), error_messages={'required': 'A avaliação é obrigatória', 'invalid': 'A avaliação deve ser um número entre 0 e 5'})