from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, desc
from datetime import date

import SQLEngine
from Model import History, Comment, Stock

# Assuming `Base` is already bound to an engine
engine = SQLEngine.engine().engine
Session = sessionmaker(bind=engine)
session = Session()

# Today's date
today = date.today()

# Query to count comments for today's histories grouped by stock code
results = (
    session.query(
        Stock.code,
        Stock.name,
        func.count(Comment.id).label("comment_count")
    )
    .join(History, Stock.code == History.stock_code)
    .join(Comment, History.id == Comment.history_id)
    .filter(History.date == today)
    .group_by(Stock.code, Stock.name)
    .order_by(desc("comment_count"))
    .limit(20)
    .all()
)

# Print results
for stock_code, stock_name, comment_count in results:
    print(f"{stock_code} ({stock_name}): {comment_count}")
