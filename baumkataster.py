import pandas
import math
import numpy 
import db_settings
import pyexasol
kataster_gelsenkirchen = "baumkataster_ge.csv"
kataster_koeln = "Bestand_Einzelbaeume_Koeln_0_repaired.csv"
kataster_wesel = "Baumkataster.csv"
kataster_wesel_json = "Baumkataster.geojson"
db = db_settings.db("biologie")



def gattungen_koeln(min_size=0):
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
    koeln = gattungen_koeln(min_size)
    gelsenkrichen = gattungen_gelsenkirchen(min_size)
    wesel = gattungen_wesel(min_size)
    alle = numpy.unique(numpy.sort(numpy.concatenate((koeln, wesel, gelsenkrichen))))
    print(alle)
    print(alle.shape)
    return alle
def check_gattung_in_db(gattungs_list):
    gattungen_in_db =numpy.array(db.export_to_pandas("""SELECT * FROM biologie.gattungen  ORDER BY id""")['WISS_NAME'])
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

    

alle = alle_gattungen()
check_gattung_in_db(alle)