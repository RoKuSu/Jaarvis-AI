import re
import sqlite3
import numpy
import pandas as pd
import flask
from flask import Flask
from flask_restful import Resource, Api
from flask_restful.utils import cors
import os
from sqlite3 import Error
import glob
import pickle
import json
from collections import defaultdict
from flask_cors import CORS
from flask import request
from shapely.geometry import Point, Polygon

app = Flask(__name__)
api = Api(app)
CORS(app, origins="http://127.0.0.1:8080", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True)


class DemandAPI(Resource):

    @cors.crossdomain(origin='*')
    def get(self):
        with open('demand.json') as json_file:
            data = json.load(json_file)

        return flask.jsonify(data)

    @cors.crossdomain(origin='*')
    def post(self):
        with open('demand.json') as json_file:
            data = json.load(json_file)

        return flask.jsonify(data)

class LiveCarsAPI(Resource):

    @cors.crossdomain(origin = '*')
    def get(self):
        vehicles_free = pd.read_json('https://evo.ca/api/Cars.aspx')
        vehicles_free['Lat'] = vehicles_free.data.apply(lambda x: x['Lat'])
        vehicles_free['Lon'] = vehicles_free.data.apply(lambda x: x['Lon'])
        vehicles_free['Lat_Lon'] = vehicles_free[['Lat','Lon']].apply(lambda x : list(x),axis = 1)
        vehicles_free = vehicles_free[['Lat_Lon']]
        vehicles_free.to_json('live_cars.json')
        with open('live_cars.json') as json_file:
            data = json.load(json_file)
        return flask.jsonify(data)

    @cors.crossdomain(origin = '*')
    def put(self):
        vehicles_free = pd.read_json('https://evo.ca/api/Cars.aspx')
        vehicles_free['Lat'] = vehicles_free.data.apply(lambda x: x['Lat'])
        vehicles_free['Lon'] = vehicles_free.data.apply(lambda x: x['Lon'])
        vehicles_free['Lat_Lon'] = vehicles_free[['Lat','Lon']].apply(lambda x : list(x),axis = 1)
        vehicles_free = vehicles_free[['Lat_Lon']]
        vehicles_free.to_json('live_cars.json')
        with open('live_cars.json') as json_file:
            data = json.load(json_file)
        return flask.jsonify(data)


class PolygonMap(Resource):
    """ fetch n points and create a polygon object.Then calculate the total number
        of the available and booked vehicles
    """

    @staticmethod
    def traverse_over_data(data: dict):
        for key, value in data.items():
            # yield {'key': key, 'value': value}
            if value.get('lat_long', False):
                yield value

    def calculate_count_with_hour(self, data: dict, polygon_obj: Polygon, hour: int) -> dict:
        """ this check on the hourly basis """

        result = {'total_available': 0.0,
                  'total_booked': 0.0,
                  'hour': hour,
                  'message': 'Above values are calculated by considering a specific hour of the day.'
                  }

        for zone_info in self.traverse_over_data(data):
            lat_long = zone_info.get('lat_long')

            if Point(lat_long[1], lat_long[0]).within(polygon_obj):

                if zone_info.get('available', False):
                    total_avail = zone_info.get('available')[hour]
                    print("avail: {}".format(float(total_avail)))
                    result['total_available'] += float(total_avail)

                if zone_info.get('booked', False):
                    total_book = zone_info.get('booked')[hour]
                    print("book: {}".format(float(total_book)))
                    result['total_booked'] += float(total_book)

                print(zone_info)

        return result

    def calculate_count(self, data: dict, polygon_obj: Polygon) -> dict:
        result = {'total_available': 0.0,
                  'total_booked': 0.0,
                  'message': 'Above values are calculated by considering the whole 24 hour data.'
                  }

        for zone_info in self.traverse_over_data(data):
            lat_long = zone_info.get('lat_long')

            if Point(lat_long[1], lat_long[0]).within(polygon_obj):

                if zone_info.get('available', False):
                    total_avail = pd.DataFrame(zone_info.get('available')).sum()
                    print("avail: {}".format(float(total_avail[0])))
                    result['total_available'] += float(total_avail[0])

                if zone_info.get('booked', False):
                    total_book = pd.DataFrame(zone_info.get('booked')).sum()
                    print("book: {}".format(float(total_book[0])))
                    result['total_booked'] += float(total_book[0])

                print(zone_info)

        return result

    @cors.crossdomain(origin='*')
    def post(self):
        resp_data = request.json
        # resp_data['points'] = ["49.323042, -123.075382",
        #                        "49.323280, -123.062764",
        #                        "49.319266, -123.061820",
        #                        "49.319252, -123.077849"]
        try:
            assert resp_data.get('points', False)
            assert isinstance(resp_data.get('points'), list)
            assert len(resp_data.get('points')) >= 3

            hour_value = resp_data.get('hour', None)
            if hour_value:
                hour_value = resp_data.get('hour', None)
                assert isinstance(hour_value, int)
                assert hour_value >= 0
                assert hour_value <= 23

            point_list = [(float(coord.split(',')[1]), float(coord.split(',')[0]))
                          for coord in resp_data.get('points')]  # point obj is (long,lat)

        except AssertionError:
            return flask.jsonify({'message': "\'points\' is mandatory fields in the request. "
                                             "points should be a string and "
                                             "at least 3 points should be given. Optional field \'hour\' : should be an"
                                             " int value between (including 0 & 23)"
                                             " 0 to 23 (represents 24 hour clock)."}), 400

        with open('demand.json') as json_file:
            data = json.load(json_file)

        polygon_obj = Polygon(point_list)

        if resp_data.get('hour', False):
            result = self.calculate_count_with_hour(data, polygon_obj, hour=hour_value)
        else:
            result = self.calculate_count(data, polygon_obj)

        return flask.jsonify(result)


api.add_resource(DemandAPI, '/evo_demand')
api.add_resource(LiveCarsAPI, '/evo_live_cars')
api.add_resource(PolygonMap, '/polygon_view')

app.run(host='0.0.0.0', port=5000)
