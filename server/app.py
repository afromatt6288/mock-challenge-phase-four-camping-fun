from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Camper, Activity, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Index(Resource):
    def get(self):
        response = make_response(
            {
                "message": "Hello Campers!"
            },
            200
        )
        return response
    
api.add_resource(Index, '/')

class Campers(Resource):
    def get(self):
        response_dict_list = []
        for n in Camper.query.all():
            response_dict_list.append(n.to_dict(only=('id', 'name', 'age')))
        response = make_response(response_dict_list, 200)
        return response

    def post(self):
        try:
            new_record = Camper(
                name=request.form.get('name'),
                age=int(request.form.get('age')), 
                )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            return make_response({"errors": [e.__str__()]}, 422)
        response = make_response(jsonify(new_record.to_dict()), 201)
        return response 

api.add_resource(Campers, '/campers')

class CampersById(Resource):
    def get(self, id):
        res = Camper.query.filter(Camper.id == id).first()
        if res:
            response_dict = res.to_dict(rules=('activities',))
            response = make_response(jsonify(response_dict, 200))
            return response
        return make_response(jsonify({"error": "Camper not found"}), 404)

api.add_resource(CampersById, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        response_dict_list = []
        for n in Activity.query.all():
            response_dict_list.append(n.to_dict())
        response = make_response(response_dict_list, 200)
        return response

api.add_resource(Activities, '/activities')

class ActivitiesById(Resource):
    def get(self, id):
        res = Activity.query.filter(Activity.id == id).first()
        if res:
            response_dict = res.to_dict()
            response = make_response(jsonify(response_dict, 200))
            return response
        return make_response(jsonify({"error": "Activity not found"}), 404)

    def patch(self, id):
        record = Activity.query.filter(Activity.id == id).first()
        if record:
            try:
                for attr in request.form:
                    setattr(record, attr, request.form.get(attr))
                db.session.add(record)
                db.session.commit()
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            response = make_response(jsonify(record.to_dict()), 201)
            return response 
        return make_response(jsonify({"error": "Activity not found"}), 404)

    def delete(self, id):
        record = Activity.query.filter(Activity.id == id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
            response_dict = {"message": "Activity successfully deleted"}
            return make_response(response_dict, 200)
        return make_response(jsonify({"error": "Activity not found"}), 404)

api.add_resource(ActivitiesById, '/activities/<int:id>')

class Signups(Resource):
    def get(self):
        response_dict_list = []
        for n in Signup.query.all():
            response_dict_list.append(n.to_dict())
        response = make_response(response_dict_list, 200)
        return response

    def post(self):
        try:
            new_record = Signup(
                time=int(request.form.get('time')),
                activity_id=int(request.form.get('activity_id')),
                camper_id=int(request.form.get('camper_id')),
                )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            return make_response({"errors": [e.__str__()]}, 422)
        response = make_response(jsonify(new_record.to_dict()['activity']), 201)
        return response 

api.add_resource(Signups, '/signups')

class SignupsById(Resource):
    def get(self, id):
        res = Signup.query.filter(Signup.id == id).first()
        if res:
            response_dict = res.to_dict()
            response = make_response(jsonify(response_dict, 200))
            return response
        return make_response(jsonify({"error": "File not found"}), 404)

    def patch(self, id):
        record = Signup.query.filter(Signup.id == id).first()
        if record:
            try:
                for attr in request.form:
                    setattr(record, attr, request.form.get(attr))
                db.session.add(record)
                db.session.commit()
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            response = make_response(jsonify(record.to_dict()), 201)
            return response 
        return make_response(jsonify({"error": "Record not found"}), 404)

    def delete(self, id):
        record = Signup.query.filter(Signup.id == id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
            response_dict = {"message": "Record successfully deleted"}
            return make_response(response_dict.to_dict(), 200)
        return make_response(jsonify({"error": "Record not found"}), 404)

api.add_resource(SignupsById, '/signups/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
