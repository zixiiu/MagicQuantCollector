import logging
import time
import datetime

import analysis.tagger
from collector import NewData
import variables
import Notification
import pysnowball as ball

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

gostright = int(variables.test_mode)

logging.info('service started.')
while True:
    try:
        if datetime.datetime.now().strftime('%H') == '00' or gostright:
            NewData.get_all_stock_code()
            NewData.update_data()
            analysis.tagger.process_stock_comments()
            # Notification.send_notification("MQCollector SUCCESS.")
        else:
            logging.debug('not the time yet. checking API availability')
            ball.set_token('xq_a_token=%s' % variables.token)
            r = ball.quote_detail('SZ300059')

        time.sleep(3600)
    except Exception as e:
        logging.exception("message")
        Notification.send_notification("MQCollector ERROR \n %s" % e.__str__())
        time.sleep(3600)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
