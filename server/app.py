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

class AllScientists(Resource):

    def get(self):
        # scientists = Scientist.query.all()
        # response_body = []
        # for scientist in scientists:
        #     scientist_dictionary = scientist.to_dict(only=('id', 'name', 'field_of_study'))
        #     response_body.append(scientist_dictionary)

        response_body = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in Scientist.query.all()]
        return make_response(response_body, 200)
    
    def post(self):
        try:
            new_scientist = Scientist(name=request.json.get('name'), field_of_study=request.json.get('field_of_study'))
            db.session.add(new_scientist)
            db.session.commit()
            response_body = new_scientist.to_dict(only=('id', 'name', 'field_of_study'))
            return make_response(response_body, 201)
        except:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

api.add_resource(AllScientists, '/scientists')

class ScientistById(Resource):

    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        
        if scientist:
            response_body = scientist.to_dict(rules=('-missions.scientist', '-missions.planet.missions'))
            return make_response(response_body, 200)
        else:
            response_body = {
                "error": "Scientist not found"
            }
            return make_response(response_body, 404)
        
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if scientist:
            try:
                for attr in request.json:
                    setattr(scientist, attr, request.json.get(attr))

                db.session.commit()
                response_body = scientist.to_dict(rules=('-missions',))
                return make_response(response_body, 202)
            except:
                response_body = {
                    'errors': ["validation errors"]
                }
                return make_response(response_body, 400)
        else:
            response_body = {
                "error": "Scientist not found"
            }
            return make_response(response_body, 404)
        
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if scientist:
            # for mission in scientist.missions:
            #     db.session.delete(mission)
            
            db.session.delete(scientist)
            response_body = {}
            return make_response(response_body, 204)
        else:
            response_body = {
                "error": "Scientist not found"
            }
            return make_response(response_body, 404)

api.add_resource(ScientistById, '/scientists/<int:id>')

class AllPlanets(Resource):

    def get(self):
        response_body = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]
        return make_response(response_body, 200)

api.add_resource(AllPlanets, "/planets")

class AllMissions(Resource):
    
    def post(self):
        try:
            new_mission = Mission(name=request.json.get('name'), scientist_id=request.json.get('scientist_id'), planet_id=request.json.get('planet_id'))
            db.session.add(new_mission)
            db.session.commit()
            response_body = new_mission.to_dict(rules=('-planet.missions', '-scientist.missions'))
            return make_response(response_body, 201)
        except:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

api.add_resource(AllMissions, "/missions")

@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
