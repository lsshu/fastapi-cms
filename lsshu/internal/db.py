from datetime import datetime
from typing import Union

from sqlalchemy import create_engine, Column, Integer, TIMESTAMP, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_SQLALCHEMY_DATABASE_URL, DB_ENGINE_KWARGS, DB_SESSION_MAKER_KWARGS

Engine = create_engine(
    DB_SQLALCHEMY_DATABASE_URL,
    **DB_ENGINE_KWARGS
)

SessionLocal = sessionmaker(bind=Engine, **DB_SESSION_MAKER_KWARGS)
# 创建基本映射类
Base = declarative_base(bind=Engine, name='Model')


def dbs():
    """
    实例 sessionmaker
    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Model(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.now, comment="创建日期")
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新日期")

    def to_dict(self):
        """
        ORM转dict
        :return:
        """
        columns = [c.name for c in self.__table__.columns] + [name for name, obj in vars(self.__class__).items() if isinstance(obj, property)]
        return {key: getattr(self, key, None) for key in columns}
