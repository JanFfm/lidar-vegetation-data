import re
from urllib import request
import numpy as np
import laspy   #needs also laszip to be installed
from pathlib import Path
import pyexasol
import pandas as pd

import tqdm
import db_settings

"""_summary_
write pandas.dataframe to db and clean it
"""
def reset(db, labels, data, table_name):
    db.import_from_pandas(data, table_name )
    db.execute("COMMIT")
    data_frame =pd.DataFrame(columns = labels) 
    id_frame = pd.DataFrame(columns = ['id'])
    frames = [id_frame, data_frame]
    data_frame = pd.concat(frames)
    return data_frame


def save_to_db(las, name, postfix):

    print(las.header)  
    #<LasHeader(1.2, <PointFormat(1, 0 bytes of extra dims)>)>
    labels = list(las.point_format.dimension_names)
    point_number = len(las.points)
    print("number of points: ", point_number)
    print(labels)
    #['X', 'Y', 'Z', 'intensity', 'return_number', 'number_of_returns', 'scan_direction_flag',  'edge_of_flight_line', 'classification', 'synthetic', 'key_point', 'withheld', 'scan_angle_rank', 'user_data', 'point_source_id', 'gps_time'] 
    #rgb gibt es in uunserer variante nicht!  'red', 'green', 'blue']

    
    data_frame =pd.DataFrame(columns = labels)
    id_frame = pd.DataFrame(columns = ['id'])
    frames = [id_frame, data_frame]
    data_frame = pd.concat(frames)
    #print(data_frame.describe())    
    db = pyexasol.connect(dsn=db_settings.connection_string, user=db_settings.username, password=db_settings.pw,schema="lidar_schema", autocommit=True) #, schema='lidar'
    #db.execute("""Create Table lidar.gelsenkichen""")
    table_name = name + "_" +str(postfix)
    #db.execute("""DROP TABLE """+table_name+"""""")
    try:
        db.execute("""DROP TABLE """+table_name+"""""")
    except:
        print("crating table ", table_name)

    request = build_request_create_table(labels, table_name)
    db.execute(request)
    db.execute("COMMIT")


    for i in tqdm.tqdm(range(point_number)):
        values = [i]  #for id
        for label in labels:
            key = las[label][i]
            values.append(key)
        data_frame.loc[len(data_frame)] = values

        

        if (i+1) % 50000 == 0:
            data_frame =reset(db, labels, data_frame, table_name)
    data_frame =reset(db, labels, data_frame, table_name)


def test():
    las = laspy.read("./gelsenkirchen/3dm_32_290_5647_1_nw.laz")
    save_to_db(las, "test", "0")

def build_request_create_table(label_list, table_name):

        

    request = """CREATE TABLE IF NOT EXISTS """+table_name+""" (id int IDENTITY PRIMARY KEY, """   
    for label in label_list:
        request = request + label + """ float, """
    
    request = request[:-2]
    request = request + """)"""

    return request




    