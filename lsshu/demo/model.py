from sqlalchemy import Column, String

from lsshu.internal.db import Model
from lsshu.internal.method import plural

name = plural(__name__.capitalize())
table_name = name.replace('.', '_')
permission = {"name": "Demo", "scope": name, "action": [{"name": "de", "scope": "de"}]}


class Models(Model):
    """ 模型 """
    __tablename__ = table_name
    name = Column(String(15), nullable=False, unique=True, comment="名称")
