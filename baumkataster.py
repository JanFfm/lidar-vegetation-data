import pandas
import numpy 
import db_settings
import tqdm
import geojson 
import re
import coord_f
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
#kataster files (not in github repro):

kataster_gelsenkirchen = "baumkataster/baumkataster_ge.csv"
kataster_koeln = "baumkataster/Bestand_Einzelbaeume_Koeln_0_repaired.csv"
kataster_wesel = "baumkataster/Baumkataster.csv"
kataster_wesel_json = "baumkataster/Baumkataster.geojson"
db = db_settings.db()
"""
funktions to read tree-kataster informations from citys Wesel, Köln, Gelsenkirchen
"""

def read_kataster_gelsenkrichen():
    """
    reads kataster of gelsenkrichen and saves to db
    """
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
            gattungs_id =db.export_to_pandas(request)
            try: 
                gattungs_id = gattungs_id['ID'][0]                
            
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
                w_request = w_request+ """("""+str(x)+""","""+str(y)+""","""+str(gattungs_id)+""","""+ str(city_code)+"""),"""
             
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

    db.execute(w_request)
    db.commit()



def read_koeln_kataster():
    """
    reads kataster-file for köln and saves all trees to db
    """
    kataster = pandas.read_csv(kataster_koeln, sep=';', encoding ='utf-8')
    
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
            gattungs_id =db.export_to_pandas(request)
            try: 
                gattungs_id = gattungs_id['ID'][0]                
            
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
                w_request = w_request+ """("""+str(x)+""","""+str(y)+""","""+str(gattungs_id)+""","""+ str(1)+"""),"""
                   

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
    maps each tree in database to lidar files db-entry of a certain city with id=city_code
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
            
            
