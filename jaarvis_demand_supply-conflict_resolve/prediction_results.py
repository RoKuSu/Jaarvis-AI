""" log file is in opt/apps/scripts/jaarvis_demand_supply/logs/demand2_output.txt """

import re
import sqlite3
import numpy
import pandas as pd
import os
from sqlite3 import Error
import glob
import pickle
import json
from collections import defaultdict

class forecasting():

    def __init__(self):

        self.zones_list = pd.read_csv('/opt/apps/Jaarvis_Demand_Supply/zones_list.csv')
        self.Sql_connection1 = self.create_connection('/opt/apps/scripts/jaarvis_demand_supply/zone_lat_log.db')
        self.lat_long_df = pd.read_sql_query("select * from zone_lat_log;", self.Sql_connection1)
        self.path1 = '/opt/apps/Jaarvis_Demand_Supply/demand_models'
        self.path2 = '/opt/apps/Jaarvis_Demand_Supply/available_models'

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database specified by the db_file :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None
        print("DB connection check..")

    def forecaster(self):
        print("forecaster method is reading the data now")
        booked = defaultdict(dict)
        available = defaultdict(dict)
        demand = defaultdict(dict)
        for x in glob.glob(os.path.join(self.path1, '*.pkl')):
            try:
                model_book = pickle.load(open(x, 'rb'))
                zone = re.findall('[a-zA-Z]\d[a-zA-Z]\s{0,1}\d{0,1}[a-zA-Z]{0,1}\d{0,1}', x)[0]
                print(zone)
                demand[zone]['booked'] = [0 if i < 0 else i for i in numpy.ceil((model_book.forecast(24)))]
                # print(self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['lat'].values[0],
                #       self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['log'].values[0])
                demand[zone]['lat_long'] = self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['lat'].values[0], \
                                           self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['log'].values[0]
            except:
                print('problem with zone ' + zone)
                pass
        for y in glob.glob(os.path.join(self.path2, '*.pkl')):
            try:
                model_free = pickle.load(open(y, 'rb'))
                zone = re.findall('[a-zA-Z]\d[a-zA-Z]\s{0,1}\d{0,1}[a-zA-Z]{0,1}\d{0,1}', y)[0]
                print(zone)
                demand[zone]['available'] = [0 if i < 0 else i for i in numpy.ceil((model_free.forecast(24)))]
                # print(self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['lat'].values[0],
                #       self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['log'].values[0])
                demand[zone]['lat_long'] = self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['lat'].values[0], \
                                           self.lat_long_df[self.lat_long_df['zone'].str.contains(zone)]['log'].values[0]

            except:
                print('problem with zone ' + zone)
                pass
        # demand['booked'] = booked
        # demand['available'] = available
        data = json.dumps(demand)
        with open('demand.json', 'w') as f:
            f.write(data)
        print('forecasting done json saved in demand.json')

forecastingObj = forecasting()
forecastingObj.forecaster()