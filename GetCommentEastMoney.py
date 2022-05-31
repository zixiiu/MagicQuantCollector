from pysnowball import utls
from Model import Comment
from datetime import datetime, timedelta
from time import sleep
import requests
from bs4 import BeautifulSoup
import logging


def getComment(symbol, page):
    # returns a tuple of (msg, time)
    url = 'http://guba.eastmoney.com/list,%s,f_%i.html' % (symbol, page)
    r = requests.get(url)
    year = (datetime.today() - timedelta(days=1)).strftime('%Y')
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup.title)
    res = []
    divs = soup.find_all("div", {"class": "normal_post"})
    if len(divs) == 0:
        raise ValueError('EastMoney Crawler Error, maybe page has changed.')
    for div in divs:
        div.find_next()
        title = div.find_next("span", {"class": "a3"})
        time = div.find_next("span", {"class": "a5"})
        post_url = title.find('a').attrs['href']
        if title.find('em') and 'icon_list_hot' in title.find('em').attrs['class']:
            pass
        else:
            res.append(
                (title.text,
                 datetime.strptime(year + '-' + time.text, '%Y-%m-%d %H:%M'),
                 post_url
                 )
            )
            # print(title.text, time.text)
    return res


def getCommentUntil(timestamp, symbol):
    cur_page = 1
    rsl = []
    id_dedup = set()
    latest_time = 0
    cur_cmt_time = datetime.now().timestamp() * 1000

    while timestamp < cur_cmt_time:
        rs = getComment(symbol, cur_page)
        logging.debug('%s: send request for EastMoney comment, page %d' % (symbol, cur_page))
        sleep(0.5)

        for txt, ptime, purl in rs:
            # print(datetime.fromtimestamp(timestamp/1000), datetime.fromtimestamp(cmt['created_at']/1000))
            cur_cmt_time = ptime.timestamp() * 1000
            if purl in id_dedup:
                continue
            id_dedup.add(purl)
            newCmt = Comment()
            newCmt.url = purl
            newCmt.text = txt
            newCmt.time = ptime
            newCmt.source = 'eastmoney'
            newCmt.added_time = datetime.now()

            if cur_cmt_time > timestamp:
                rsl.append(newCmt)

            latest_time = cur_cmt_time if latest_time < cur_cmt_time else latest_time

        cur_page += 1
    return rsl, latest_time


if __name__ == "__main__":
    rs = getCommentUntil(1653984950000.0,'002594')
    print(rs)
