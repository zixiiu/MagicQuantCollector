import datetime

from sqlalchemy import select

from collector import GetCommentEastMoney, GetCommentXueqiu
import Notification
from SQLEngine import engine
from sqlalchemy.orm import Session, sessionmaker
from Model import Stock, History
import pysnowball as ball
import tushare as ts

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
    em_failed = False
    with Session(e) as s:
        stmt = select(Stock)
        symbols = s.scalars(stmt).all()  # Retrieve all symbols first to get total count
        total_symbols = len(symbols)

        start_time = datetime.now()  # Record the start time before the loop

        for i, sym in enumerate(symbols, start=1):
            elapsed_time = datetime.now() - start_time
            # Format elapsed time as HH:MM:SS
            elapsed_str = str(elapsed_time).split('.')[0]  # Remove microseconds
            logging.info('[%d/%d p:%s] %s: start getting comment', i, total_symbols, elapsed_str, sym.code)

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
                newHis.comments += new_cmts_xq
                try:
                    new_cmts_em, latest_time_em = GetCommentEastMoney.getCommentUntil(load_until, sym.code_em)
                    logging.info('%s: %d new comments acquired from eastmoney.' % (sym.code, len(new_cmts_em)))
                    newHis.comments += new_cmts_em
                    em_failed = True
                except ValueError:
                    logging.warning('EastMoney failed on %s. Maybe invalid code' % sym.code)

                sym.latest_comment = datetime.fromtimestamp(max(latest_time_xq, latest_time_em) / 1000)

                sym.histories.append(newHis)
                sym.updated = today
                # count!
                n_cmt_xq += len(new_cmts_xq)
                n_cmt_em += len(new_cmts_em)
                n_stock += 1

            else:
                logging.info('%s: today already recorded, skip.' % sym.code)
            s.commit()
    if n_cmt_xq > 0 or n_cmt_em > 0:
        Notification.send_notification(
            'MQCollector SUCCESS \n %i xueqiu cmts and %i EastMoney cmts acquired for %i stocks \n '
            'Time used %s' % (
                n_cmt_xq, n_cmt_em, n_stock, elapsed_str))
        if em_failed:
            Notification.send_notification('SOME EastMoney failed to parse. Pay attention.')


def get_all_stock_code():
    pro = ts.pro_api(variables.ts_key)
    # Pull stock data from tushare API
    logging.info('starting to get all stock code')
    df = pro.stock_basic(
        ts_code="",
        name="",
        exchange="",
        market="\u4e3b\u677f",  # Specifies main board stocks in Chinese
        is_hs="",
        list_status="",
        limit="",
        offset=""
    )

    # Only get the necessary fields
    stock_data = df[['ts_code']]

    # Create a SQLAlchemy session
    Session = sessionmaker(bind=engine().engine)
    session = Session()

    try:
        # Iterate over each row in the DataFrame
        added_stock = 0
        for _, row in stock_data.iterrows():
            ts_code = row['ts_code']

            # Format the code and code_em fields
            code_em = ts_code.split('.')[0]  # Extract only the digits part
            market_code = ts_code.split('.')[1]  # Extract the market code part
            code = f"{market_code}{code_em}"  # Concatenate market code and digit part

            # Check if the stock already exists in the database
            existing_stock = session.query(Stock).filter_by(code=code).first()
            if existing_stock:
                continue

            # Create a new Stock object
            stock = Stock(
                code=code,
                code_em=code_em
            )

            # Add the stock to the session
            session.add(stock)
            added_stock += 1
            logging.info(f"Added new stock with code {code}.")

        # Commit all the changes to the database
        session.commit()
        logging.info("%i new stocks added." % added_stock)
        if added_stock:
            Notification.send_notification("NEW STOCK: %i new stocks added." % added_stock)


    except Exception as e:
        session.rollback()  # Rollback in case of any errors
        logging.error("Error occurred while adding stocks:", exc_info=True)

    finally:
        session.close()  # Close the session


if __name__ == '__main__':
    # update_data()
    get_all_stock_code()
