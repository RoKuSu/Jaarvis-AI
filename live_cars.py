import sqlite3
from sqlite3 import Error
import json
from flask import Flask
from collections import defaultdict
from flask_cors import CORS

# mathematics libraries
import pandas as pd
import numpy as np

def create_connection(db_file):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file)
            print("connection to DB file successful!.....")
            return conn
        except Error as e:
            print(e)
        return None


app = Flask(__name__)
CORS(app)

@app.route('/live_cars')
def live_cars_result():
    
    global new_dict
    Sql_connection3 = create_connection('/opt/apps/scripts/jaarvis_demand_supply/zone_lat_log.db')
    cursor = Sql_connection3.cursor()

    vehicles_free = pd.read_json('https://evo.ca/api/Cars.aspx')
    vehicles_free['Lat'] = vehicles_free.data.apply(lambda x: x['Lat'])
    vehicles_free['Lon'] = vehicles_free.data.apply(lambda x: x['Lon'])
    vehicles_free['Lat_Lon'] = vehicles_free[['Lat','Lon']].apply(lambda x : list(x),axis = 1)
    vehicles_free = vehicles_free[['Lat_Lon']]
    vehicles_free.to_json('live_cars.json')
    with open('live_cars.json') as json_file:
        data = json.load(json_file)
    return flask.jsonify(data)
    
if __name__ == '__main__':
   app.run(host= '0.0.0.0', port = 5002)


# import sqlite3
# from sqlite3 import Error
# import json
# import flask
# from collections import defaultdict
# from flask_cors import CORS

# # mathematics libraries
# import pandas as pd
# import numpy as np

# from mapbox import Geocoder

# new_dict = defaultdict(dict)

# def create_connection(db_file):
#         """ create a database connection to the SQLite database
#             specified by the db_file
#         :param db_file: database file
#         :return: Connection object or None
#         """
#         try:
#             conn = sqlite3.connect(db_file)
#             print("connection to DB file successful!.....")
#             return conn
#         except Error as e:
#             print(e)
#         return None

# def reverse_geocode(x):
#     zipcode=''
#     geocoder = Geocoder(
#         access_token="pk.eyJ1IjoiYXNoaXNoa3VtYXJjc2dvIiwiYSI6ImNqbWx1amFsNTAzd2QzcmtnZHE4c2JjZ2IifQ.OD4QxBXxKDKqvBY_RDZgtg")
#     '''
#         if the token gets expired create a new one from "https://www.mapbox.com/"
#     '''
#     resp = geocoder.reverse(x[1], x[0])
#     # resp = geocoder.reverse(-123.123,49.123)
#     json_veh = json.loads(resp.text)

#     for info in json_veh.get('features')[0].get('context'):
#         if "postcode" in info.get('id',False):
#             zipcode = info.get('text')
#     print(zipcode)
#     return zipcode

# def zone_lat_long(x):
    
#     if x[1]!='':
#         try:
#             return [lat_long_df[lat_long_df['zone'].str.contains(x[1])]['lat'].values[0],lat_long_df[lat_long_df['zone'].str.contains(x[1])]['log'].values[0]]
#         except:
#             return x[0]
#     else:
#         return x[0]

    
# def live_cars(x):
#     global new_dict
#     new_dict[x[0]]['lat_long'] = x[1]
#     new_dict[x[0]]['live_cars'] = x[2]

    
# def type_conversion(x):
#     if type(x)== list:
#         return tuple(x)
#     else:
#         print(x)

# from flask import Flask
# app = Flask(__name__)
# CORS(app)

# @app.route('/live_cars')
# def live_cars_result():
    
#     global new_dict
#     Sql_connection3 = create_connection('/opt/apps/scripts/jaarvis_demand_supply/zone_lat_log.db')
#     cursor = Sql_connection3.cursor()

#     vehicles_free = pd.read_json('https://evo.ca/api/Cars.aspx')
#     vehicles_free['Lat'] = vehicles_free.data.apply(lambda x: x['Lat'])
#     vehicles_free['Lon'] = vehicles_free.data.apply(lambda x: x['Lon'])
#     vehicles_free['Lat_Lon'] = vehicles_free[['Lat','Lon']].apply(lambda x : list(x),axis = 1)

#     print("data loaded successfully!....")

#     print("finding postal codes of all zones. It may take upto 10 minutes.....")
#     vehicles_free['zone'] = vehicles_free['Lat_Lon'].apply(lambda x: reverse_geocode(x))
#     print("reverse_geocoding successful!.....")

#     vehicles_free = vehicles_free[['zone','Lat_Lon']]

#     lat_long_df = pd.read_sql_query('select * from zone_lat_log;',Sql_connection3)

#     vehicles_free['zone_lat_long'] = vehicles_free['Lat_Lon']

#     vehicles_free1 = vehicles_free.groupby(['zone']).count().sort_values(by='Lat_Lon')[::-1]

#     vehicles_free1 = vehicles_free1.reset_index()

#     print("mapping cars lat longs to postal codes ")
#     vehicles_free['zone_lat_long'] =vehicles_free[['Lat_Lon','zone']].apply(lambda x: zone_lat_long(list(x)),axis=1)

#     vehicles_free = pd.merge(vehicles_free,vehicles_free1,how='left',on = 'zone')
#     vehicles_free = vehicles_free.drop(['Lat_Lon_x','Lat_Lon_y'],axis=1)

#     vehicles_free = vehicles_free.rename(columns={'zone_lat_long_x':'zone_lat_long','zone_lat_long_y':'live_cars'})
    
#     print("converting data into json!.....")
#     vehicles_free = vehicles_free[['zone','zone_lat_long','live_cars']].apply(lambda x: live_cars(list(x)),axis=1)

#     print(new_dict)
#     with open('live_cars.json', 'w') as f:
#         f.write(json.dumps(new_dict))
    

#     with open('live_cars.json') as json_file:
#         data = json.load(json_file)
#     return flask.jsonify(data)
    
# if __name__ == '__main__':
#    app.run(host= '0.0.0.0', port = 5001)