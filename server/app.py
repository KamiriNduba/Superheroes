#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Absolute path to the directory containing this script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database URI, defaulting to a SQLite database in the same directory as this script
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app
app = Flask(__name__)

# Configure database URI and track modifications
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Route to create a new hero_power relationship
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    # Extract JSON data from the request
    data = request.get_json()
    
    # Extract required fields from the JSON data
    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')
    
    # Check if all required fields are provided
    if not all([strength, power_id, hero_id]):
        return make_response({"errors": ["Missing required fields"]}, 400)
    
    # Validate strength value
    if strength not in ['Strong', 'Weak', 'Average']:
        return make_response({"errors": ["validation errors"]}, 400)
    
    # Retrieve hero and power objects from the database
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)
    
    # Check if hero and power exist
    if hero is None or power is None:
        return make_response({"errors": ["Hero or Power not found"]}, 404)
    
    # Create a new hero_power relationship
    hero_power = HeroPower(strength=strength, hero=hero, power=power)
    
    try:
        db.session.add(hero_power)
        db.session.commit()
    except Exception as e:
        return make_response({"errors" : str(e)}, 400)
    
    # Construct response data
    response_data = {
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
    }
    
    # Create a response with the constructed data
    response = make_response(response_data, 200)
    return response


# Route to update a power's description
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    # Retrieve power object by ID
    power = Power.query.get(id)
    
    # Check if power exists
    if power is None:
        return make_response({"error": "Power not found"}, 404)
    
    # Extract updated description from JSON data
    data = request.get_json()
    
    # Check if description is provided
    if 'description' in data:
        new_description = data['description']
        
        # Validate new description length
        if len(new_description) < 20:
            return make_response({"errors": ["validation errors"]}, 400)
        
        # Update power's description and commit changes to the database
        try:
            power.description = new_description
            db.session.commit()
        except ValueError as e:
            return make_response({"errors" : str(e)}, 400)
    
    # Construct updated power data
    updated_power = {
        "id": power.id,
        "name": power.name,
        "description": power.description
    }
    
    # Create a response with the updated power data
    response = make_response(updated_power, 200)
    return response


# Route to retrieve a power by ID
@app.route('/powers/<int:id>')
def get_power(id):
    # Retrieve power object by ID
    power = Power.query.get(id)
    
    # Check if power exists
    if power is None:
        return make_response({"error": "Power not found"}, 404)
    
    # Construct power data
    power_dict = {
        "id": power.id,
        "name": power.name,
        "description": power.description
    }
    
    # Create a response with the power data
    response = make_response(power_dict, 200)
    return response


# Route to retrieve all powers
@app.route('/powers')
def get_powers():
    # Retrieve all powers from the database
    powers = Power.query.all()
    
    # Construct a list of power dictionaries
    powers_list = []
    for power in powers:
        power_dict = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        powers_list.append(power_dict)
    
    # Create a response with the list of power dictionaries
    response = make_response(powers_list, 200)
    return response


# Route to retrieve a hero by ID
@app.route('/heroes/<int:id>')
def get_hero(id):
    # Retrieve hero object by ID
    hero = Hero.query.get(id)
    
    # Check if hero exists
    if hero is None:
        return make_response({"error": "Hero not found"}, 404)
    
    # Construct hero data
    hero_dict = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": []
    }
    
    # Populate hero_powers list with associated power data
    for hero_power in hero.hero_powers:
        power = {
            "id": hero_power.power.id,
            "name": hero_power.power.name,
            "description": hero_power.power.description
        }
        
        hero_power_dict = {
            "id": hero_power.id,
            "hero_id": hero_power.hero_id,
            "power": power,
            "power_id": hero_power.power_id,
            "strength": hero_power.strength
        }
        
        hero_dict["hero_powers"].append(hero_power_dict)
        
    # Create a response with the hero data
    return make_response(hero_dict, 200)


# Route to retrieve all heroes
@app.route('/heroes')
def get_heroes():
    # Retrieve all heroes from the database
    heroes = Hero.query.all()
    
    # Construct a list of hero dictionaries
    heroes_list = []
    for hero in heroes:
        hero_dict = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        }
        heroes_list.append(hero_dict)
    
    # Create a response with the list of hero dictionaries
    response = make_response(heroes_list, 200)
    return response


# Route for the index page
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


# Entry point for the application
if __name__ == '__main__':
    # Run the application on port 5555 in debug mode
    app.run(port=5555, debug=True)
