from matplotlib.pyplot import get
import db_settings

def get_class(id):
    family = dict_families[dict_gattung[id]['ID_FAMILIE']]
    order = dict_order[family['ID_ORDNUNG']]
    c = order['ID_KLASSE']
    return c
def get_order(id):
    family = dict_families[dict_gattung[id]['ID_FAMILIE']]
    o = family['ID_ORDNUNG']
    return o
def get_family(id):
    f = dict_gattung[id]['ID_FAMILIE']
    return f


db =db_settings.db(autocommit=False)
req_families = """SELECT * FROM lidar_proj.familien"""
req_order = """SELECT * FROM lidar_proj.ordnungen"""
req_class = """SELECT * FROM lidar_proj.klassen"""
req_gattung = """SELECT * FROM lidar_proj.gattungen"""
req_trees = """SELECT * FROM lidar_proj.trees"""

df_families = db.export_to_pandas(req_families)
df_order = db.export_to_pandas(req_order)
df_class = db.export_to_pandas(req_class)
df_gattung = db.export_to_pandas(req_gattung)
df_trees = db.export_to_pandas(req_trees)

df_families.set_index("ID", drop=True, inplace=True)
df_order.set_index("ID", drop=True, inplace=True)
df_class.set_index("ID", drop=True, inplace=True)
df_gattung.set_index("ID", drop=True, inplace=True)
df_trees.set_index("ID", drop=True, inplace=True)

global dict_gattung
global dict_families
global dict_order
global dict_class
global dict_trees

dict_gattung =df_gattung.to_dict(orient="index")
dict_families =df_families.to_dict(orient="index")
dict_order =df_order.to_dict(orient="index")
dict_class =df_class.to_dict(orient="index")
dict_trees = df_trees.to_dict(orient="index")

#print(get_class(116))
#print(get_order(116))
#print(get_family(116))
#print(dict_gattung)
#print(dict_trees)
