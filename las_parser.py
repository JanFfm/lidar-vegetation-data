import numpy as np
import laspy   #needs also laszip to be installed
from pathlib import Path
import pyexasol
import pandas as pd

import tqdm


"""_summary_
write pandas.dataframe to db and clean it
"""
def reset(data):
    print(data)
    db.import_from_pandas(data, 'gelsenkirchen')
    db.execute("COMMIT")
    data_frame =pd.DataFrame(columns = labels) 
    return data_frame

path="./gelsenkirchen"

#read all .laz from current working dir
las_file_path = []
for file in Path(path).glob('*.laz'):
    #print(file.name)
    las_file_path.append(file)
    
    
#they are in PRDF1-format
    
las = laspy.read(las_file_path[0])
las
print("###2")
print(las.header)  
#<LasHeader(1.2, <PointFormat(1, 0 bytes of extra dims)>)>
labels = list(las.point_format.dimension_names)
point_number = len(las.points)
print("number of points: ", point_number)
print(labels)
#['X', 'Y', 'Z', 'intensity', 'return_number', 'number_of_returns', 'scan_direction_flag',  'edge_of_flight_line', 'classification', 'synthetic', 'key_point', 'withheld', 'scan_angle_rank', 'user_data', 'point_source_id', 'gps_time'] 
#rgb gibt es in uunserer variante nicht!  'red', 'green', 'blue']


data_frame =pd.DataFrame(columns = labels)
#print(data_frame.describe())    
db = pyexasol.connect(dsn="192.168.56.101:8563", user="sys", password="exasol", schema='lidar', autocommit=True)
#db.execute("""Create Table lidar.gelsenkirchen""")
db.execute("""DROP TABLE gelsenkirchen""")
db.execute("""CREATE TABLE IF NOT EXISTS gelsenkirchen (
    X int,
    Y int,
    Z int,
    intensity int,
    return_number int, 
    number_of_returns int,
    scan_direction_flag float,
    edge_of_flight_line float,
    classification int,
    synthetic float,
    key_point float,
    withheld float,
    scan_angle_rank int,
    user_data int,
    point_source_id int,
    gps_time float   
    
    
    )""")
db.execute("COMMIT")


for i in tqdm.tqdm(range(point_number)):
    values = []
    for label in labels:
        key = las[label][i]
        values.append(key)
    data_frame.loc[len(data_frame)] = values

    

    if (i+1) % 1000 == 0 or (i+1) == point_number:
        data_frame =reset(data_frame)

        



    