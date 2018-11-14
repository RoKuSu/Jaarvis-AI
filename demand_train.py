#!/usr/bin/env python
# coding: utf-8
import numpy
import sklearn
import dateutil
import sqlite3
from sqlite3 import Error
from sklearn import preprocessing
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor

class DemandTrain:

    def __init__(self):
        self.Sql_connection1 = self.create_connection('/home/dineshb/PycharmProjects/jaarvis_demand_supply/evo.db')
        self.df = pd.read_sql_query("select * from zones;", self.Sql_connection1)

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

    def data_cleansing(self):
        from dateutil.parser import parse

        self.df.time = [(x or "0:00") for x in self.df.time]
        self.df['time'] = pd.Series(pd.DatetimeIndex(self.df['time']).hour)

        return self.df

    def feature_addition(self):
        # no feature added
        pass

    def feature_elimination(self):
        #no feature deleted
        pass

    def training_data(self):

        le = preprocessing.LabelEncoder()
        le = le.fit(self.df.zone)

        self.df['zone'] = le.transform(self.df.zone.get_values())

        X = self.df[['zone', 'year', 'month', 'week', 'day', 'time']]
        X = X.values
        demand = self.df.booked_vehicles.fillna(self.df.booked_vehicles.mean()).values
        free_vehicles = self.df.free_vehicles.fillna(self.df.free_vehicles.mean()).values

        return X, demand, free_vehicles

    def train(self):
        X, demand, free_vehicles = self.training_data()
        regressor_demand = RandomForestRegressor(n_estimators=10, random_state=0)
        regressor_demand.fit(X, demand)
        regressor_available = RandomForestRegressor(n_estimators=10, random_state=0)
        regressor_available.fit(X, free_vehicles)
        pickle.dump(regressor_demand, open("demand_ML_model.sav", 'wb'))
        pickle.dump(regressor_available, open("free_vehicles_ML_model.sav", 'wb'))

    def demand_predict(self, year, month, day, hour, pickupzone, avg_no_vehicle_7_days):
        regressor=self.train()
        return regressor.predict([[year,month,day,hour,pickupzone,avg_no_vehicle_7_days]])
