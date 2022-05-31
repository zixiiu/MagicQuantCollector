import requests
import variables
import logging

def send_notification(content):
    try:
        url = 'https://api2.pushdeer.com/message/push?pushkey=%s&text=%s' %(variables.push_key, content)
        requests.get(url)
    except Exception:
        logging.error('NOTIFICATION FAILED')
        pass

if __name__ == '__main__':
    send_notification('test_notification')