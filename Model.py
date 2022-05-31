from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Numeric
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Stock(Base):
    __tablename__ = "stock"
    code = Column(String(30), primary_key=True)
    code_em = Column(String(30))
    name = Column(String(30))
    updated = Column(Date)
    started = Column(Date)
    latest_comment = Column(DateTime)
    histories = relationship(
        "History", back_populates="stock", cascade="all, delete-orphan",
        lazy='select'
    )
    # def __repr__(self):
    #     return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    stock_code = Column(String(30), ForeignKey('stock.code'), nullable=False)
    date = Column(Date)
    timestamp = Column(DateTime)
    price = Column(Numeric(precision=30, scale=10))
    change = Column(Numeric(precision=30, scale=10))
    volume = Column(Numeric(precision=30, scale=10))
    amount = Column(Numeric(precision=30, scale=10))
    market_cap = Column(Numeric(precision=30, scale=10))

    stock = relationship("Stock", back_populates='histories')

    comments = relationship(
        "Comment", back_populates='history', cascade='all, delete-orphan',
        lazy='noload'
    )


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    text = Column(Text(1048576), nullable=False)
    type = Column(String(10))
    source = Column(String(10))
    time = Column(DateTime)
    added_time = Column(DateTime)
    encoding = Column(String(1024))
    url = Column(String(512))

    history_id = Column(Integer, ForeignKey("history.id"), nullable=False)
    history = relationship("History", back_populates="comments")

    # def __repr__(self):
    #     return f"Address(id={self.id!r}, email_address={self.email_address!r})"


if __name__ == '__main__':
    ## CREATE SCHEMA
    from SQLEngine import engine
    engine = engine().engine
    Base.metadata.create_all(engine)