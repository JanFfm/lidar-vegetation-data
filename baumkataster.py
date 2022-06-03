import pandas
import math
import numpy 
kataster_gelsenkirchen = "baumkataster_ge.csv"
kataster_koeln = "Bestand_Einzelbaeume_Koeln_0_repaired.csv"
kataster_wesel = "Baumkataster.csv"
kataster_wesel_json = "Baumkataster.geojson"




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

gattungen_gelsenkirchen()