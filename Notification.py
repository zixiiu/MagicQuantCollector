import requests
import variables

def send_notification(content):
    try:
        url = 'https://api2.pushdeer.com/message/push?pushkey=%s&text=%s' %(variables.push_key, content)
        requests.get(url)
    except Exception:
        pass

if __name__ == '__main__':
    send_notification('test_notification')