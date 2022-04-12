from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_SQLALCHEMY_DATABASE_URL, DB_ENGINE_KWARGS, DB_SESSION_MAKER_KWARGS

Engine = create_engine(
    DB_SQLALCHEMY_DATABASE_URL,
    **DB_ENGINE_KWARGS
)

SessionLocal = sessionmaker(bind=Engine, **DB_SESSION_MAKER_KWARGS)
# 创建基本映射类
Model = declarative_base(bind=Engine, name='Model')


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


def to_dict(self):
    """
    ORM转dict
    :param self:
    :return:
    """
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


Model.to_dict = to_dict
Model.dbs = dbs
