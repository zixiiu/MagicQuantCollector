import os

token = os.environ['TOKEN']
db_address = os.environ['DB_ADDRESS']
db_username = os.environ['DB_USERNAME']
db_pw = os.environ['DB_PASSWORD']
# log_file_name = os.environ['LOG_FILE_NAME']
push_key = os.environ['PUSH_KEY']
test_mode = os.environ['TEST_MODE'] if 'TEST_MODE' in os.environ else 1
ts_key = os.environ['TS_KEY']