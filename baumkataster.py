import pandas
import math

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
    gattungs_list = kataster['Gattung'].unique()
    print(gattungs_list)
    print(gattungs_list.shape)
    return gattungs_list

gattungen_koeln()