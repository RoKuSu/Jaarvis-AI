import flask
import pickle
import pandas as pd
import json
from flask import Flask, request
from flask_restful import Resource, Api, fields, marshal_with

app = Flask(__name__)
api = Api(app)

class DemandAPI(Resource):

    def __init__(self):
        self.demand_model = pickle.load(open('demand_ML_model.sav', 'rb'))
        self.free_vehicles_model = pickle.load(open('free_vehicles_ML_model.sav', 'rb'))
        # self.year=0
        # self.month=0
        # self.day=0
        # self.hour=0
        # self.zone=0

# @app.route('/<string:name>', methods=['POST', 'GET'])
    def get(self, year, month, day, hour, zone, avg_veh_7_days):
        pass
        # return str(self.Pred_obj.demand_predict(year, month, day, hour, zone))


    def post(self):
        try:
            data = request.get_json(silent=True)
            year = data['year']
            month = data['month']
            week = data['week']
            day = data['day']
            hour = data['hour']
            zone = data['zone']

        except:
            print("put request expected json, other format given ")

        try:
            year = request.args.get('year')
            month = request.args.get('month')
            week = request.args.get('week')
            day = request.args.get('day')
            hour = request.args.get('hour')
            zone = request.args.get('zone')

        except:
            print("put request expected string query, other format given")

        df = pd.read_csv('zones_list.csv')
        df.year = year
        df.month = month
        df.week = week
        df.day = day
        df.hour = hour
        df.zone = zone


        X_test = df.values
        pred_demand = self.demand_model.predict(X_test)
        pred_free_vehicles = self.free_vehicles_model.predict(X_test)
        df['demand'] = pred_demand
        df['free_vehicles'] = pred_free_vehicles
        return flask.jsonify({'demand': json.dumps(dict(zip(df['zone'], df['booked_vehicles']))),
                              'available_cars': json.dumps(dict(zip(df['zone'], df['free_vehicles'])))})

api.add_resource(DemandAPI, '/demand')

app.run(port=5000)
