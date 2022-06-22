from lidar_file_class import LidarFileData

class LidarExasolData(LidarFileData):
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name