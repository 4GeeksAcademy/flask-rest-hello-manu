"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    users=User.query.all()
    if users == []:
        return jsonify({"msg":"there are no registered users"}), 404
    response_body = [item.serialize() for item in users]
    return jsonify(response_body), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_id(user_id):
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return jsonify({"msg":"user doesn't exist"}), 404
    return jsonify(user.serialize()), 200

@app.route('/people', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    if characters == []:
        return jsonify({"msg":"no characters found"}), 404
    response_body = [item.serialize() for item in characters]
    return jsonify(response_body), 200

@app.route('/people/<int:character_id>', methods=['GET'])
def get_character_id(character_id):
    character = Character.query.filter_by(id = character_id).first()
    if character is None:
        return jsonify({"msg":"character doesn't exist"}), 404
    return jsonify(character.serialize()), 200

@app.route('/planet', methods=['GET'])
def get_planet():
    planets = Planet.query.all()
    if planets == []:
        return jsonify({"msg":"no planets found"}), 404
    response_body = [item.serialize() for item in planets]
    return jsonify(response_body), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    planet = Planet.query.filter_by(id = planet_id).first()
    if planet is None:
        return jsonify({"msg":"planet doesn't exist"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/favorite', methods=['GET'])
def get_favorite():
    favorites = Favorite.query.all()
    if favorites == []:
        return jsonify({"msg":"no favorites found"}), 404
    response_body = [item.serialize() for item in favorites]
    return jsonify(response_body), 200

@app.route('/favorite/<int:favorite_id>', methods=['GET'])
def get_favorite_id(favorite_id):
    favorite = Favorite.query.filter_by(id = favorite_id).first()
    if favorite is None:
        return jsonify({"msg":"favorite doesn't exist"}), 404
    return jsonify(favorite.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def post_favorite_planet(planet_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email = email).one_or_none()
    if user == None:
        return jsonify({"msg": "user doesn't exist"}), 404
    planet = Planet.query.get(planet_id)
    if planet == None:
        return jsonify({"msg": "planet doesn't exist"}), 404    
    new_favorite = Favorite()
    new_favorite.user = user
    new_favorite.planet = planet

    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 200

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def post_favorite_character(character_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email = email).one_or_none()
    if user == None:
        return jsonify({"msg": "user doesn't exist"}), 404
    character = Character.query.get(character_id)
    if character == None:
        return jsonify({"msg": "character doesn't exist"}), 404
    new_favorite = Favorite()
    new_favorite.user = user
    new_favorite.character = character
    
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_fv(planet_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg":"user doesn't exist"}),404
    planet = Planet.query.get(planet_id)
    if planet == None:
        return jsonify({"msg":"character doesn't exist"}),404
    favorite_delete = Favorite.query.filter_by(user_id=user.id, planet_id=planet.id).first()
    if favorite_delete == None:
        return jsonify({"msg":"favorite doesn't exist"}),404
    
    db.session.delete(favorite_delete)
    db.session.commit()
    return jsonify({"msg":"item deleted successfully"}), 200

@app.route('/favorite/people/<int:character_id>', methods=['DELETE'])
def delete_character_fv(character_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email = email).one_or_none()
    if user == None:
        return jsonify({"msg":"user doesn't exist"}),404
    character = Character.query.get(character_id)
    if character == None:
        return jsonify({"msg":"character doesn't exist"}),404
    favorite_delete = Favorite.query.filter_by(user_id=user.id, character_id=character.id).first()
    if favorite_delete == None:
        return jsonify({"msg":"favorite doesn't exist"}),404
    
    db.session.delete(favorite_delete)
    db.session.commit()
    return jsonify({"msg":"deletion successful"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)