from sqlalchemy import create_engine
import variables


class engine():
    def __init__(self):
        # test
        # db_path = "mysql+pymysql://%s:%s@%s/TestQuantDB?charset=utf8mb4"
        # production
        db_path = "mysql+pymysql://%s:%s@%s/mq_prod?charset=utf8mb4"
        self.engine = create_engine \
            (db_path %
             (variables.db_username, variables.db_pw, variables.db_address))
