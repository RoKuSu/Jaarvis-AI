#!/usr/bin/env python
# coding: utf-8

'''demand_train.py creates SARIMA models for all the zones we want to predict demand for'''
""" log file is in opt/apps/scripts/jaarvis_demand_supply/logs/demand1_output.txt """

import numpy
import datetime
import sqlite3
from sqlite3 import Error
from sklearn import preprocessing
import pandas as pd
import pickle
import statsmodels.api
import glob
import pickle
import json
from collections import defaultdict
import os


class DemandTrain:
    def __init__(self):
        # try:
        #     if platform.system() == 'Windows':
        self.Sql_connection1 = self.create_connection('/opt/apps/scripts/jaarvis_demand_supply/evo.db')

        #     elif platform.system() == 'Linux':
        #         self.Sql_connection1 = self.create_connection('/opt/apps/scripts/jaarvis_demand_supply/evo.db')
        # except Error as e:
        #     print(e)

        self.df = pd.read_sql_query("select * from zones order by id;", self.Sql_connection1)

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
        print('DB connection is done')
        return None

    def data_cleansing(self):
        print('data_cleansing started')
        self.df.booked_vehicles = self.df.booked_vehicles.fillna(0)
        self.df.free_vehicles = self.df.free_vehicles.fillna(0)
        self.df = self.df.dropna(how='any')
        self.df = self.df[~self.df.astype(str).eq('None').any(1)]
        self.df = self.df.mask(self.df.eq('None')).dropna()
        self.df = self.df[~self.df.zone.apply(lambda x: str(x).isdigit())]
        self.df.time = self.df.time.astype(str).str[:2].astype(int)
        self.df.time = self.df.time.replace(regex=True, to_replace=r'\D', value=r'')
        self.df = self.df.sort_values(['zone', 'year', 'month', 'week', 'day', 'time'], ascending=True)
        self.df['date'] = self.df[['year', 'month', 'day']].apply(lambda x: '-'.join(x.dropna().astype(str).values),
                                                                    axis=1)
        self.df = self.df.drop(['id', 'year', 'month', 'week', 'day'], axis=1)
        self.df['date'] = self.df[['date', 'time']].apply(lambda x: ' '.join(x.dropna().astype(str).values), axis=1)
        self.df['date'] = self.df[['date', 'time']].apply(lambda x: x.astype(str) + ':00:00', axis=1)
        self.df = self.df.sort_values(['date', 'zone'])
        print('data cleansing finished')
        return self.df

    def feature_addition(self):
        # no feature added
        print('feature addition started')
        train_df = self.data_cleansing()
        train_booked_df = pd.pivot_table(train_df, values=['booked_vehicles'], index=['date'], columns=['zone'])
        train_free_df = pd.pivot_table(train_df, values=['free_vehicles'], index=['date'], columns=['zone'])
        train_booked_df = train_booked_df.fillna(0)
        train_free_df = train_free_df.fillna(0)
        train_booked_df = train_booked_df.booked_vehicles
        train_free_df = train_free_df.free_vehicles
        booked_df = train_booked_df.reindex(
            pd.date_range(start='2018-11-16 14:00:00', end=train_booked_df.index[-1], freq='H'))
        free_df = train_free_df.reindex(
            pd.date_range(start='2018-11-16 14:00:00', end=train_free_df.index[-1], freq='H'))
        booked_df = booked_df[~booked_df.index.isin(train_booked_df.index)]
        free_df = free_df[~free_df.index.isin(train_free_df.index)]
        train_booked_df = pd.concat([train_booked_df, booked_df])
        train_free_df = pd.concat([train_free_df, free_df])
        print('features added')
        return train_booked_df, train_free_df

    def feature_elimination(self):
        # no feature deleted
        pass

    def training_data(self):
        print('making training data')
        train_booked_df, train_free_df = self.feature_addition()
        train_booked_df = train_booked_df.iloc[pd.to_datetime(train_booked_df.index).values.argsort()]
        train_free_df = train_free_df.iloc[pd.to_datetime(train_free_df.index).values.argsort()]
        train_booked_df = train_booked_df.fillna(0)
        train_free_df = train_free_df.fillna(0)
        train_booked_df.index = pd.to_datetime(train_booked_df.index) - pd.Timedelta(hours=5)
        train_free_df.index = pd.to_datetime(train_free_df.index) - pd.Timedelta(hours=5)

        pd.DataFrame({'zone': self.df['zone'].unique()}).to_csv("zones_list.csv")
        print('training data ready for modeling')
        return train_booked_df, train_free_df

    def train(self):
        
        train_booked_df, train_free_df = self.training_data()
        path1 = '/opt/apps/Jaarvis_Demand_Supply/demand_models/'
        path2 = '/opt/apps/Jaarvis_Demand_Supply/available_models/'
        print('training started')
        os.chdir(path1)
        for x in train_booked_df.keys():
            try:

                model = statsmodels.api.tsa.SARIMAX(train_booked_df[x][-171:-171 + 168], order=(1, 0, 1),
                                                    seasonal_order=(1, 1, 0, 24), enforce_stationarity=False)
                model = model.fit(method='ncg',disp=False)
                model = model.save(str(x) + '.pkl')
            except:

                print(x, 'demand model not created', )

        print('demand_models_created')

        os.chdir(path2)
        for y in train_free_df.keys():
            try:

                model = statsmodels.api.tsa.SARIMAX(train_free_df[y][-171:-171 + 168], order=(1, 0, 1),
                                                    seasonal_order=(1, 1, 0, 24), enforce_stationarity=False)
                model = model.fit(method='ncg',disp=False)
                model = model.save(str(y) + '.pkl')
            except:
                print(y, 'available model not created')
        print('available_models_created\ntraining finished')


TrainingObj = DemandTrain()
TrainingObj.train()