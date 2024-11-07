from pysnowball import utls
from Model import Comment
from datetime import datetime
from time import sleep
import logging
import pysnowball as ball
import variables



def getComment(symbol, page):
    count = 20
    comment_url = 'https://xueqiu.com/query/v1/symbol/search/status.json?' \
                  'count=%d&comment=0&symbol=%s&hl=0&source=user&sort=time&page=%d&q=&type=11' \
                  % (count, symbol, page)
    r = utls.fetch(comment_url, host='xueqiu.com')
    # type
    # 0 regular post
    # 3 long blog
    # empty RT@
    # 2 post with pic

    return r['list'], r['maxPage']


def getCommentUntil(timestamp, symbol):
    cur_page = 1
    rsl = []
    id_dedup = set()
    latest_time = 0
    cur_cmt_time = datetime.now().timestamp() * 1000

    while timestamp < cur_cmt_time:
        rs, mp = getComment(symbol, cur_page)
        logging.debug('%s: send request for xueqiu comment, page %d' % (symbol, cur_page))
        sleep(0.5)
        max_page = mp

        for cmt in rs:
            # print(datetime.fromtimestamp(timestamp/1000), datetime.fromtimestamp(cmt['created_at']/1000))
            cur_cmt_time = cmt['created_at']
            if cmt['id'] in id_dedup:
                continue
            id_dedup.add(cmt['id'])
            newCmt = Comment()
            newCmt.type = int(cmt['type']) if len(cmt['type']) else None
            newCmt.text = cmt['text']
            newCmt.time = datetime.fromtimestamp(cmt['created_at'] / 1000)
            newCmt.source = 'xueqiu'
            newCmt.added_time = datetime.now()
            if cur_cmt_time > timestamp:
                rsl.append(newCmt)
            latest_time = cmt['created_at'] if latest_time < cmt['created_at'] else latest_time

        if max_page == cur_page:
            break
        cur_page += 1
    return rsl, latest_time

if __name__ == '__main__':
    ball.set_token('xq_a_token=%s' % variables.token)
    rs = getComment('SZ300059', 1)
    print(rs)