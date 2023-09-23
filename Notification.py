import requests
import variables
import logging

def send_notification(title, content = ''):
    try:
        url = 'https://sctapi.ftqq.com/%s.send?title=%s&desp=%s' %(variables.push_key, title, content)
        requests.get(url)
    except Exception:
        logging.error('NOTIFICATION FAILED')
        pass

if __name__ == '__main__':
    send_notification('test_title', 'test_content')