import datetime

from sqlalchemy import select

import Notification
from SQLEngine import engine
from sqlalchemy.orm import Session
from Model import Stock, History, Comment
import pysnowball as ball
import GetComment

from datetime import date, datetime, timedelta
import variables

import logging

def update_data():
    ball.set_token(variables.token)
    ## this is the sql engine
    e = engine().engine
    ## get interested stocks

    # count cmts:
    n_cmt = 0
    n_stock = 0
    with Session(e) as s:
        stmt = select(Stock)
        for sym in s.scalars(stmt):
            logging.info('%s: starting...' % sym.code)
            today = date.today()
            meta = ball.quote_detail(sym.code)

            name = meta['data']['quote']['name']
            sym.name = name

            newHis = History()
            newHis.price = meta['data']['quote']['current']
            newHis.change = meta['data']['quote']['chg']
            newHis.volume = meta['data']['quote']['volume']
            newHis.amount = meta['data']['quote']['amount']
            newHis.market_cap = meta['data']['quote']['market_capital']
            newHis.timestamp = datetime.now()
            newHis.date = date.today()

            if sym.started is None:
                sym.started = today

            if sym.updated is None or sym.updated < today:
                ## add comment for newHis
                if sym.latest_comment is None:
                    load_until = datetime.now() - timedelta(days=3)
                    load_until = load_until.timestamp() * 1000
                else:
                    load_until = sym.latest_comment.timestamp() * 1000
                newCmts, latest_time = GetComment.getCommentUntil(load_until, sym.code)
                logging.info('%s: %d new comments acquired.' % (sym.code, len(newCmts)))
                newHis.comments += newCmts
                sym.latest_comment = datetime.fromtimestamp(latest_time / 1000)

                sym.histories.append(newHis)
                sym.updated = today
                # count!
                n_cmt += len(newCmts)
                n_stock += 1

            else:
                logging.info('%s: today already recorded, skip.' % sym.code)
        logging.info('%s: saving to db.' % sym.code)
        s.commit()
    Notification.send_notification('MQCollector SUCCESS: %i cmts acquired for %i stocks' %(n_cmt, n_stock))

if __name__ == '__main__':
    update_data()
