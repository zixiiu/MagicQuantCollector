import requests
import logging
import json

import variables


def send_notification(content):
    try:
        url = 'https://open.feishu.cn/open-apis/bot/v2/hook/%s' % variables.push_key
        headers = {'Content-Type': 'application/json'}
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raises an error for non-2xx responses
    except Exception as e:
        logging.error('NOTIFICATION FAILED: %s', e)

if __name__ == '__main__':
    send_notification('test_notification')
