import datetime

from sqlalchemy import select

import GetCommentEastMoney
import Notification
from SQLEngine import engine
from sqlalchemy.orm import Session
from Model import Stock, History, Comment
import pysnowball as ball
import GetCommentXueqiu

from datetime import date, datetime, timedelta
import variables

import logging


def update_data():
    ball.set_token('xq_a_token=%s' % variables.token)
    ## this is the sql engine
    e = engine().engine
    ## get interested stocks

    # count cmts:
    n_cmt_xq = 0
    n_cmt_em = 0
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
                new_cmts_xq, latest_time_xq = GetCommentXueqiu.getCommentUntil(load_until, sym.code)
                logging.info('%s: %d new comments acquired from xueqiu.' % (sym.code, len(new_cmts_xq)))
                new_cmts_em, latest_time_em = GetCommentEastMoney.getCommentUntil(load_until, sym.code_em)
                logging.info('%s: %d new comments acquired from eastmoney.' % (sym.code, len(new_cmts_em)))
                newHis.comments += new_cmts_xq
                newHis.comments += new_cmts_em

                sym.latest_comment = datetime.fromtimestamp(max(latest_time_xq, latest_time_em) / 1000)

                sym.histories.append(newHis)
                sym.updated = today
                # count!
                n_cmt_xq += len(new_cmts_xq)
                n_cmt_em += len(new_cmts_em)
                n_stock += 1

            else:
                logging.info('%s: today already recorded, skip.' % sym.code)
        logging.info('%s: saving to db.' % sym.code)
        s.commit()
    if n_cmt_xq > 0 or n_cmt_em > 0:
        Notification.send_notification('MQCollector SUCCESS: %i xueqiu cmts and %i EastMoney acquired for %i stocks' % (
            n_cmt_xq, n_cmt_em, n_stock))


if __name__ == '__main__':
    update_data()
