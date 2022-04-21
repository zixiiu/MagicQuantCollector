from sqlalchemy import create_engine
import variables

class engine():
    def __init__(self):
        self.engine = create_engine\
            ("mysql+pymysql://%s:%s@%s/MainQuantDB?charset=utf8mb4" %
             (variables.db_username, variables.db_pw, variables.db_address))