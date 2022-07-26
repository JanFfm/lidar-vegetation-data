import pyexasol



connection_string =""  
username= "" 
pw= "" 
os_username= ""

def db(autocommit=True):    
    """ opens connection to exasol-database
        
        part of .gitignore
    
    """
    return pyexasol.connect(dsn=connection_string, user=username, password=pw, autocommit=autocommit, client_os_username=os_username) 

