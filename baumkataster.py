import pandas
import math
import numpy 
import db_settings
import pyexasol
import tqdm
import geojson 
import re
import coord_f
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
kataster_gelsenkirchen = "baumkataster/baumkataster_ge.csv"
kataster_koeln = "baumkataster/Bestand_Einzelbaeume_Koeln_0_repaired.csv"
kataster_wesel = "baumkataster/Baumkataster.csv"
kataster_wesel_json = "baumkataster/Baumkataster.geojson"
db = db_settings.db()
"""
funktions to read tree-kataster informations from citys Wesel, Köln, Gelsenkirchen
"""



def read_kataster_gelsenkrichen():
    kataster = pandas.read_csv(kataster_gelsenkirchen, sep=';', encoding ='utf-8')
    kataster = kataster[kataster.BAUMART != 'NaN']
    city_code = 2
    
    w_request = """INSERT INTO lidar_proj.trees (x,y,ID_GATTUNG, CITY_ID) VALUES"""
    gattungen = {
    }
    counter = 0
    for index, row in tqdm.tqdm(kataster.iterrows()):
        
    
        x = row['X']
        x =float(x.replace(',', '.'))

        y = row['Y']
        y =float(y.replace(',', '.'))


        gattung= str(row['BAUMART']).lower().split(' ')[0]
        gattung = re.sub(r"[\n\t\s]*", "", gattung)
        if gattung in gattungen:
            gattungs_id = gattungen[gattung]
        else: 
            request = """SELECT gattungen.id FROM lidar_proj.gattungen WHERE LOWER(TRIM(gattungen.lat_name))=\'""" + gattung + """\'"""
            #print(request)
            gattungs_id =db.export_to_pandas(request)
            try: 
                gattungs_id = gattungs_id['ID'][0]
                
            
            #print(gattungs_id)
            except:
                print("search typo " , gattung)
                request = """SELECT ID_GATTUNG FROM lidar_proj.typos_gattungen WHERE LOWER(TRIM(typo))=\'""" + gattung + """\'"""
                gattungs_id =db.export_to_pandas(request)
                try:
                    gattungs_id = gattungs_id['ID_GATTUNG'][0]
                except:
                    print("cant find ", gattung)
                    gattungs_id = None
            gattungen[gattung] = gattungs_id

        
        if gattung != 'NaN' and gattungs_id != None:
                #try:
                w_request = w_request+ """("""+str(x)+""","""+str(y)+""","""+str(gattungs_id)+""","""+ str(city_code)+"""),"""
                   

                #except:
                #    print(x,y, "doppelung -> delete!")
                #    request ="""DELETE FROM lidar_proj.trees WHERE x=""" +str(x)+"""and y=""" + str(y)
                #    db_trees.execute(request)
                counter += 1
                if counter == 500:
                    counter = 0
                    w_request = w_request[:-1]
                    db.execute(w_request)
                    db.commit()
                    print("commit")
                    w_request = """INSERT INTO lidar_proj.trees (x,y,ID_GATTUNG, CITY_ID) VALUES"""

    w_request = w_request[:-1]
    print(w_request)
    #db_trees = db_settings.db("baeume")

    db.execute(w_request)
    db.commit()



def gattungen_koeln(min_size=0):    
    """_summary_

    Returns:
        _type_: _description_
    """
    kataster = pandas.read_csv(kataster_koeln, sep=';', encoding ='utf-8')
    kataster = kataster[kataster.Gattung != 'NaN']
    kataster = kataster[kataster.HöHE > min_size]
    print(kataster.describe())
    #print(kataster)
    gattungs_list = numpy.sort(kataster['Gattung'].unique())
    print(gattungs_list)
    print(gattungs_list.shape)
    return gattungs_list


def gattungen_gelsenkirchen(min_size=0):
    """_summary_

    Args:
        min_size (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    kataster = pandas.read_csv(kataster_gelsenkirchen, sep=';', encoding ='utf-8')
    kataster = kataster[kataster.BAUMART != 'NaN']
    #kataster = kataster[kataster.HOEHE > min_size or kataster.HOEHE =='NaN']
    print(kataster.describe())
    print(kataster)
    arten_list = numpy.sort(kataster['BAUMART'].unique())
    print(arten_list)
    print(arten_list.shape)
    gattungs_list = numpy.unique(numpy.array([arten_list[i].split(' ')[0] for i in range(len(arten_list))]))
    print(gattungs_list)
    print(gattungs_list.shape)
    return gattungs_list

def gattungen_wesel(min_size=2):
    """_summary_

    Args:
        min_size (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    kataster = pandas.read_csv(kataster_wesel, sep=';', encoding ='utf-8')
    kataster = kataster[kataster.GATTUNG != 'NaN']
    kataster = kataster[kataster.BAUMHOEHE > min_size]
    print(kataster.describe())
    #print(kataster)
    gattungs_list = numpy.sort(kataster['GATTUNG'].unique())
    print(gattungs_list)
    print(gattungs_list.shape)
    return gattungs_list

def alle_gattungen(min_size=2):
    """_summary_

    Args:
        min_size (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    koeln = gattungen_koeln(min_size)
    gelsenkrichen = gattungen_gelsenkirchen(min_size)
    wesel = gattungen_wesel(min_size)
    alle = numpy.unique(numpy.sort(numpy.concatenate((koeln, wesel, gelsenkrichen))))
    print(alle)
    print(alle.shape)
    return alle
def check_gattung_in_db(gattungs_list):
    gattungen_in_db =numpy.array(db.export_to_pandas("""SELECT * FROM lidar_proj.gattungen  ORDER BY id""")['LAT_NAME'])
    print(gattungen_in_db)
    not_in_db =numpy.empty(0)
    in_db =numpy.empty(0)
    for i in range(len(gattungs_list)):
        if gattungs_list[i] in gattungen_in_db:
            in_db = numpy.append(in_db,(gattungs_list[i]) )
        else:
            not_in_db = numpy.append(not_in_db,(gattungs_list[i]) )
    print("in db: ", in_db, in_db.shape)
    print("not in db: ", not_in_db, not_in_db.shape)
    return not_in_db



def read_koeln_kataster():
     """
    reads kataster-file for köln and saves all trees to db
    """
    kataster = pandas.read_csv(kataster_koeln, sep=';', encoding ='utf-8')
    #kataster = kataster[kataster.X_Koordina,kataster.Y_Koordina, kataster.Gattung, 1]
    
    w_request = """INSERT INTO lidar_proj.trees (x,y,ID_GATTUNG, CITY_ID) VALUES"""
    gattungen = {
    }
    counter = 0
    for index, row in tqdm.tqdm(kataster.iterrows()):
        
    
        x = row['X_Koordina']

        y = row['Y_Koordina']

        gattung= str(row['Gattung']).lower()
        gattung = re.sub(r"[\n\t\s]*", "", gattung)
        if gattung in gattungen:
            gattungs_id = gattungen[gattung]
        else: 
            request = """SELECT gattungen.id FROM lidar_proj.gattungen WHERE LOWER(TRIM(gattungen.lat_name))=\'""" + gattung + """\'"""
            #print(request)
            gattungs_id =db.export_to_pandas(request)
            try: 
                gattungs_id = gattungs_id['ID'][0]
                
            
            #print(gattungs_id)
            except:
                print("search typo " , gattung)
                request = """SELECT ID_GATTUNG FROM lidar_proj.typos_gattungen WHERE LOWER(TRIM(typo))=\'""" + gattung + """\'"""
                gattungs_id =db.export_to_pandas(request)
                try:
                    gattungs_id = gattungs_id['ID_GATTUNG'][0]
                except:
                    print("cant find ", gattung)
                    gattungs_id = None
            gattungen[gattung] = gattungs_id

        
        if gattung != 'NaN' and gattungs_id != None:
                #try:
                w_request = w_request+ """("""+str(x)+""","""+str(y)+""","""+str(gattungs_id)+""","""+ str(1)+"""),"""
                   

                #except:
                #    print(x,y, "doppelung -> delete!")
                #    request ="""DELETE FROM lidar_proj.trees WHERE x=""" +str(x)+"""and y=""" + str(y)
                #    db_trees.execute(request)
                counter += 1
                if counter == 500:
                    counter = 0
                    w_request = w_request[:-1]
                    db.execute(w_request)
                    db.commit()
                    print("commit")
                    w_request = """INSERT INTO lidar_proj.trees (x,y,ID_GATTUNG, CITY_ID) VALUES"""

    w_request = w_request[:-1]
    print(w_request)
    #db_trees = db_settings.db("baeume")

    db.execute(w_request)
    db.commit()
 


def read_kataster_wesel():
    """
    reads kataster-file for wesel and saves all trees to db
    """
    with open(kataster_wesel_json) as kataster_file:
        gj = geojson.load(kataster_file)
    w_request = """INSERT INTO lidar_proj.trees (x,y,ID_GATTUNG, CITY_ID) VALUES"""
    gattungen = {
    }
    counter = 0
    for tree in gj['features']:
        x, y = tree['geometry']['coordinates']
        gattung =  str(tree['properties']['GATTUNG']).lower()
        gattung = re.sub(r"[\n\t\s]*", "", gattung)
        if gattung in gattungen:
                gattungs_id = gattungen[gattung]
        else: 
            request = """SELECT gattungen.id FROM lidar_proj.gattungen WHERE LOWER(TRIM(gattungen.lat_name))=\'""" + gattung + """\'"""
            #print(request)
            gattungs_id =db.export_to_pandas(request)
            try: 
                gattungs_id = gattungs_id['ID'][0]
                
            
            #print(gattungs_id)
            except:
                print("search typo" , gattung,".")
                request = """SELECT ID_GATTUNG FROM lidar_proj.typos_gattungen WHERE LOWER(TRIM(typo))=\'""" + gattung + """\'"""
                print(request)
                gattungs_id =db.export_to_pandas(request)
                try:
                   gattungs_id = gattungs_id['ID_GATTUNG'][0]
                except:
                    print("cant find '", gattung, "'")
                    gattungs_id = None
            gattungen[gattung] = gattungs_id

        
        if gattung != 'NaN' and gattungs_id != None:
                #try:
                x, y, _, _ = coord_f.lat_long_to_utm(y,x)
                w_request = w_request+ """("""+str(x)+""","""+str(y)+""","""+str(gattungs_id)+""","""+ str(3)+"""),"""
                   

                #except:
                #    print(x,y, "doppelung -> delete!")
                #    request ="""DELETE FROM lidar_proj.trees WHERE x=""" +str(x)+"""and y=""" + str(y)
                #    db_trees.execute(request)
                counter += 1
                if counter == 500:
                    counter = 0
                    w_request = w_request[:-1]
                    db.execute(w_request)
                    db.commit()
                    print("commit")
                    w_request = """INSERT INTO lidar_proj.trees (x,y,ID_GATTUNG, CITY_ID) VALUES"""

    w_request = w_request[:-1]
    print(w_request)
    #db_trees = db_settings.db("baeume")

    db.execute(w_request)
    db.commit()
 



def compare_kataster_lidar_mapping(city_code=3):
    """
    maps each tree in database to lidar files of a certain city with id=city_code
    """
    request = """SELECT * FROM lidar_proj.trees WHERE city=""" + str(city_code)

    trees =db.export_to_pandas(request)
    request = """SELECT * FROM lidar.lidar_files WHERE city=""" + str(city_code)
    files =db.export_to_pandas(request)


    x_max = numpy.array(files['X_MAX'])
    x_min = numpy.array(files['X_MIN'])
    y_max = numpy.array(files['Y_MAX'])
    y_min = numpy.array(files['Y_MIN'])
    file_polygons = []
    for i in range(len(x_max)):
        point_list = [Point(x_min[i], y_min[i]), Point(x_max[i], y_min[i]),Point(x_max[i], y_max[i]),Point(x_min[i], y_max[i])]
        file_polygons.append(Polygon(point_list))
    tree_points = []
    for x,y in zip(trees['X'], trees['Y']):
        tree_points.append(Point(x,y))
    for tree in tree_points:
        for p in file_polygons:
            p.contains(tree)
            
            
        

#compare_kataster_lidar_mapping()

    
        
#read_kataster_wesel()
    
#read_kataster_gelsenkrichen()
