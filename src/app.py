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
from models import db, User, Charaters, Planet, FavoritesCharacters
from sqlalchemy import select
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/people', methods=['GET'])
def get_peoples():
    all_people = db.session.execute(select(Charaters)).scalars().all()
    response_body = list(map(lambda char: char.serialize(), all_people))

    return jsonify(response_body), 200

@app.route('/people/<int:position>', methods=['GET'])
def get_people(position):
    person = db.session.get(Charaters, position)
    if person == None:
        return jsonify("This person does not exist"), 404
    print(person.serialize())
    response_body = person.serialize()

    return jsonify(response_body), 200

@app.route('/people/', methods=['POST'])
def create_people():
    body = request.json
    people = Charaters(**body)
    db.session.add(people)
    db.session.commit()
    response_body = {
        "msg": "Hello, this is your POST /people/' response ",
        "chat": body
    }

    return jsonify(response_body), 200

@app.route('/planet', methods=['GET'])
def get_planets():

    all_planets = db.session.execute(select(Planet)).scalars().all()
    response_body = list(map(lambda planet: planet.serialize(), all_planets))

    return jsonify(response_body), 200

@app.route('/planet/<int:position>', methods=['GET'])
def get_planet(position):
    planet = db.session.get(Planet, position)
    if planet == None:
        return jsonify("This planet does not exist"), 404
    response_body = planet.serialize()

    return jsonify(response_body), 200

@app.route('/planet/', methods=['POST'])
def create_planet():
    body = request.json
    planet = Planet(**body)
    db.session.add(planet)
    db.session.commit()
    response_body = {
        "msg": "Hello, this is your POST /planet/' response ",
        "chat": body
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def get_users():
    all_users = db.session.execute(select(User)).scalars().all()
    response_body = list(map(lambda user: user.serialize(), all_users))

    return jsonify(response_body), 200

""" @app.route('/users/1/favorites', methods=['GET'])
def get_users_favorites(position):
    user_favorites = db.db.session.get(FavoritesCharacters, 1)
    
    response_body = ""
    return jsonify(response_body) """

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_fav_planet(planet_id):
    user = db.session.get(User, 1)
    planet = db.session.get(Planet, planet_id)
    user.favPlanets.append(planet)
    db.session.commit()
    response_body = user.serialize()

    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_planet(planet_id):
    user = db.session.get(User, 1)
    planet = db.session.get(Planet, planet_id)
    user.favPlanets.remove(planet)
    db.session.commit()
    response_body = user.serialize()

    return jsonify(response_body), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def create_fav_char(people_id):
    user = db.session.get(User, 1)
    people = db.session.get(Charaters, people_id)
    
    favChar = FavoritesCharacters(user=user, char=people) # Te voy a ser honesto, tuve que preguntarle a la IA porque me daba errores primero de  
    db.session.add(favChar)                               # TypeError y despúes de recursividad, y era que estaba pasando intentando devolver
                                                          # el favChar.serialize(), pero esa variable tiene instancias de Character y Users y peta
    db.session.commit()
    response_body = {
        "success": "character was added succesfully to favorites",
        "fav": {
            "favChar": favChar.id,
            "user_id": user.id,
            "char_id": people.id
        }
    }

    return jsonify(response_body), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_fav_char(people_id):
    user = db.session.get(User, 1)
    people = db.session.execute(select(FavoritesCharacters).where(FavoritesCharacters.char_id == people_id)).scalar_one_or_none()
    print("people ",people)
    db.session.delete(people)
    db.session.commit()
    print(user)
    response_body = {
        "msg": "The character has been deleted from the favorites list",
        "user": user.serialize()
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
