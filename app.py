import os
import sys

from datetime import datetime
from flask import Flask,request, jsonify, make_response
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

api = Api(app)

parser = reqparse.RequestParser()
db_path = os.path.join('/app/db', 'calander.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calanderdb.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def serialize(self):
        return {"id": self.id,
                "time": self.time,
                "description": self.description}
    
    def change_date_format(self, datetime_format):
        event_datetime = datetime.strptime(self.time, '%Y-%m-%dT%H:%M:%S')
        self.time = event_datetime.strftime(datetime_format)
        return self

with app.app_context():
    db.create_all()

resource_fields =  {"id": fields.Integer,
                "time": fields.String,
                "description": fields.String }

class AddEvent(Resource):
  
    def post(self):
        data = request.json

        if not data:
            return make_response(jsonify({
                "error": "Invalid Request",
                "message": "The request body must contain JSON data with 'time' and 'description'."
            }), 400)

        if 'time' not in data:
            return make_response(jsonify({
                "error": "Missing 'time'",
                "message": "Please provide the 'time' field in your request. The format should be 'YYYY-MM-DDTHH:MM:SS'."
            }), 400)

        if 'description' not in data:
            return make_response(jsonify({
                "error": "Missing 'description'",
                "message": "Please provide the 'description' field to describe the event."
            }), 400)
        
        try:
            event_datetime = datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return make_response(jsonify({
                "error": "Invalid 'time' format",
                "message": "The 'time' format is incorrect. Please use the following format: 'YYYY-MM-DDTHH:MM:SS'."
            }), 400)

        event = Event(time=event_datetime.strftime('%Y-%m-%dT%H:%M:%S'), description=data['description'].strip())

        db.session.add(event)
        db.session.commit()

        return make_response(jsonify({
            "message": "Event added successfully!",
            "event": event.serialize()
        }), 201)


class EventById(Resource):
    def get(self, event_id):

        datetime_format = request.args.get('datetime_format')  # Get the datetime_format query parameter

        try:
            event = Event.query.filter(Event.id == event_id).first()

            if event is None:
                return make_response(jsonify({'error': f'No event found with ID {event_id}'}), 404)

            if datetime_format:
                try:
                    event.time = event.change_date_format(datetime_format).time
                except ValueError as e:
                    return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400

            return make_response(jsonify(event.serialize()), 200)

        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)


class Events(Resource):

    def get_events(self, datetime_format = '%Y-%m-%dT%H:%M:%S'):
        data_store = Event.query.all()
        formated_events = [e.change_date_format(datetime_format) for e in data_store]
        
        if len(data_store) == 0:
            return jsonify({
                "message": "No events found. You can add events by posting to /add_event."
            }), 200

        return make_response(jsonify(events=[e.serialize() for e in formated_events]), 200)


    def get(self):
        datetime_format = request.args.get('datetime_format')
        from_time_str = request.args.get('from_time')
        to_time_str = request.args.get('to_time')

        if from_time_str is None and to_time_str is None:
            if datetime_format is None:
                return self.get_events()
            else:
                return self.get_events(datetime_format)

        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            from_time = datetime.strptime(from_time_str, '%Y-%m-%dT%H:%M:%S') if from_time_str else today
            to_time = datetime.strptime(to_time_str, '%Y-%m-%dT%H:%M:%S') if to_time_str else datetime.now()

            events = Event.query.all()

            filtered_events = []
            for event in events:
                try:
                    event_datetime = datetime.strptime(event.time, '%Y-%m-%dT%H:%M:%S')
                    if from_time <= event_datetime <= to_time:

                        if datetime_format:
                            formatted_datetime = event_datetime.strftime(datetime_format)
                            event.time = formatted_datetime
                        filtered_events.append(event)
                except ValueError:
                    continue

            return make_response(jsonify(events=[e.serialize() for e in filtered_events]), 200)

        except Exception as e:
            return jsonify({'error': str(e)}), 500


api.add_resource(AddEvent, '/add_event')
api.add_resource(EventById, '/events/<int:event_id>')
api.add_resource(Events, '/events')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(debug=False)