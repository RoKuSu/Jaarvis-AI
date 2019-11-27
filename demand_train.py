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
import platform
import os


class DemandTrain:
    def __init__(self):
        # try:
        #     if platform.system() == 'Windows':
        self.Sql_connection1 = self.create_connection('evo.db')

        #     elif platform.system() == 'Linux':
        #         self.Sql_connection1 = self.create_connection('/opt/apps/scripts/jaarvis_demand_supply/evo.db')
        # except Error as e:
        #     print(e)

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
        self.df = self.df.dropna(how='any')
        self.df.time = self.df.time.str[:2].astype(int)
        self.df.time = self.df.time.replace(regex=True, inplace=True, to_replace=r'\D', value=r'')
        self.df.time = [(x or -1) for x in self.df.time]
        self.df.zone = [(x or 'unknown') for x in self.df.zone]
        self.df.year = [(x or 0) for x in self.df.year]
        self.df.month = [(x or 0) for x in self.df.month]
        self.df.week = [(x or 0) for x in self.df.week]
        self.df.day = [(x or 0) for x in self.df.day]
        self.df.booked_vehicles = [(x or 0) for x in self.df.booked_vehicles]
        self.df.free_vehicles = [(x or 0) for x in self.df.free_vehicles]

        self.df = self.df.mask(self.df.eq('None')).dropna()
        self.df = self.df.fillna(0)

        return self.df

    def feature_addition(self):
        # no feature added
        pass

    def feature_elimination(self):
        # no feature deleted
        pass

    def training_data(self):

        self.data_cleansing()

        le = preprocessing.LabelEncoder()
        le = le.fit(self.df.zone)
        numpy.save('classes.npy', le.classes_)
        pd.DataFrame({'zone': self.df['zone'].unique()}).to_csv("zones_list.csv")
        self.df['zone'] = le.transform(self.df.zone.get_values())

        X = self.df[['zone', 'year', 'month', 'week', 'day', 'time']]
        X = X.values
        demand = self.df.booked_vehicles.values
        free_vehicles = self.df.free_vehicles.values

        return X, demand, free_vehicles

    def train(self):
        X, demand, free_vehicles = self.training_data()
        regressor_demand = RandomForestRegressor(n_estimators=1000, random_state=0)
        regressor_demand.fit(X, demand)
        regressor_available = RandomForestRegressor(n_estimators=1000, random_state=0)
        regressor_available.fit(X, free_vehicles)
        pickle.dump(regressor_demand, open("demand_RF_model.sav", 'wb'))
        pickle.dump(regressor_available, open("free_vehicles_RF_model.sav", 'wb'))

    def demand_predict(self, year, month, day, hour, pickupzone, avg_no_vehicle_7_days):
        # return regressor.predict([[year,month,day,hour,pickupzone,avg_no_vehicle_7_days]])
        pass


TrainingObj = DemandTrain()
TrainingObj.train()