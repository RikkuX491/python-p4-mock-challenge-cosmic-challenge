#!/usr/bin/env python3

import ipdb

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Scientists(Resource):

    def get(self):
        scientists = Scientist.query.all()
        response_body = [scientist.to_dict() for scientist in scientists]
        
        # response_body = []
        # for scientist in scientists:
        #     response_body.append(scientist.to_dict())
        
        return make_response(jsonify(response_body), 200)
    
    def post(self):
        try:
            json_data = request.get_json()
            new_scientist = Scientist(name=json_data.get('name'), field_of_study=json_data.get('field_of_study'))
            db.session.add(new_scientist)
            db.session.commit()
            response_body = new_scientist.to_dict()
            return make_response(jsonify(response_body), 201)

        except ValueError:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(jsonify(response_body), 400)

api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):

    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if not scientist:
            response_body = {
                "error": "Scientist not found"
            }
            return make_response(jsonify(response_body), 404)
        
        response_body = scientist.to_dict()
        missions_list = []
        for mission in scientist.missions:
            mission_dict = mission.to_dict()
            mission_dict.update({
                "planet": mission.planet.to_dict()
            })
            missions_list.append(mission_dict)
        response_body.update({
            "missions": missions_list
        })
        return make_response(jsonify(response_body), 200)
    
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if not scientist:
            response_body = {
                "error": "Scientist not found"
            }
            return make_response(jsonify(response_body), 404)
        
        try:
            json_data = request.get_json()
            for key in json_data:
                setattr(scientist, key, json_data.get(key))
            db.session.commit()
            response_body = scientist.to_dict()
            return make_response(jsonify(response_body), 202)

        except ValueError:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(jsonify(response_body), 400)
        
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if not scientist:
            response_body = {
                "error": "Scientist not found"
            }
            return make_response(jsonify(response_body), 404)
        
        # for mission in scientist.missions:
        #     db.session.delete(mission)

        db.session.delete(scientist)
        db.session.commit()

        response_body = {}

        return make_response(jsonify(response_body), 204)

api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):

    def get(self):
        planets = Planet.query.all()

        response_body = []
        for planet in planets:
            response_body.append(planet.to_dict())

        return make_response(jsonify(response_body), 200)

api.add_resource(Planets, '/planets')

class Missions(Resource):

    def post(self):
        try:
            json_data = request.get_json()
            new_mission = Mission(name=json_data.get('name'), scientist_id=json_data.get('scientist_id'), planet_id=json_data.get('planet_id'))
            db.session.add(new_mission)
            db.session.commit()
            response_body = new_mission.to_dict()
            response_body.update({
                "planet": new_mission.planet.to_dict(),
                "scientist": new_mission.scientist.to_dict()
            })
            return make_response(jsonify(response_body), 201)
        except ValueError:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(jsonify(response_body), 400)

api.add_resource(Missions, '/missions')

@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
