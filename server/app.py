#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os
from flask_cors import CORS

# Set up the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database migrations
migrate = Migrate(app, db)

# Initialize the database with the app context
db.init_app(app)
CORS(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Route to get all heroes
@app.route('/heroes')
def heroes():
    heroes = Hero.query.all()
    response = [hero.to_dict(only=("id", "name", "super_name")) for hero in heroes]
    return make_response(response, 200)

# Route to get a hero by ID
@app.route('/heroes/<int:id>')
def heroes_by_id(id):
    # Query the Hero model for a hero with the given ID
    hero = Hero.query.filter_by(id=id).first()
    
    # If the hero does not exist, return a 404 error
    if not hero:
        error_body = {"error": "Hero not found"}
        return make_response(error_body, 404)
    
    # If the hero exists, return the hero's details as JSON
    return make_response(hero.to_dict(), 200)

# Route to get all powers
@app.route('/powers')
def powers():
    powers = Power.query.all()
    response = [power.to_dict(only= ("description", "id", "name")) for power in powers]
    return make_response(response, 200)

# Route to get or update a power by ID
@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def powers_by_id(id):
    # Query the Power model for a power with the given ID
    power = Power.query.filter_by(id=id).first()
    
    if request.method == "GET":
        if power:
            response = power.to_dict(only=("description", "id", "name"))
            return make_response(response,200)
        else:
            return  make_response({"error": "Power not found"}, 404)

    elif request.method == "PATCH":
        if not power:
            return make_response({"error": "Power not found"}, 404)
        data = request.get_json() if request.is_json else request.form
        try:
            for key, value in data.items():
                setattr(power, key, value)
            db.session.commit()
            return make_response(power.to_dict(), 200)
        except ValueError:
            return  make_response({"errors": ["validation errors"]}, 400)


# Route for managing HeroPower relationships
@app.route('/hero_powers', methods=['POST'])
def hero_powers():
    try:
        data = request.get_json() if request.is_json else request.form
        hero_power = HeroPower(**data)
        db.session.add(hero_power)
        db.session.commit()
        return make_response(hero_power.to_dict(), 200)
    except ValueError:
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)