import logging
import time
import datetime
import NewData
import variables
import Notification

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

gostright = True

logging.info('service started.')
while True:
    try:
        if datetime.datetime.now().strftime('%H') == '00' or gostright:
            NewData.update_data()
            # Notification.send_notification("MQCollector SUCCESS.")
        else:
            logging.debug('not the time yet.')
        time.sleep(3600)
    except Exception as e:
        logging.exception("message")
        Notification.send_notification("MQCollector ERROR, check log.")
        time.sleep(3600)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
