from sqlalchemy import Column, String, Boolean, Text, Integer
from sqlalchemy_mptt.mixins import BaseNestedSets

from lsshu.internal.db import Model, Engine


class _ModelOAuthUsers(Model, BaseNestedSets):
    """登录用户"""
    __abstract__ = True
    username = Column(String(15), nullable=False, unique=True, index=True, comment="名称")
    password = Column(String(128), nullable=False, comment="密码")
    user_phone = Column(String(11), nullable=True, comment="手机")
    available = Column(Boolean, default=1, comment="是否有效")


class _ModelOAuthRoles(Model, BaseNestedSets):
    """角色"""
    __abstract__ = True
    name = Column(String(15), nullable=False, unique=True, comment="名称")
    scopes = Column(Text, nullable=False, comment="Scope")


class _ModelOAuthPermissions(Model, BaseNestedSets):
    """ 权限 """
    __abstract__ = True
    name = Column(String(15), nullable=False, comment="名称")
    icon = Column(String(20), nullable=True, comment="ICO")
    scope = Column(String(50), nullable=False, unique=True, comment="Scope")
    path = Column(String(50), nullable=False, comment="Path")
    is_menu = Column(Boolean, default=True, comment="是否为菜单")
    is_action = Column(Boolean, default=True, comment="是否为动作权限")


class _ModelOAuthAnnexes(Model):
    """ 附件 """
    __abstract__ = True
    filename = Column(String(50), nullable=False, comment="文件名")
    content_type = Column(String(100), nullable=False, comment="类型")
    path = Column(String(100), nullable=True, comment="路径")
    md5 = Column(String(32), nullable=True, comment="md5", index=True)
    size = Column(Integer, nullable=False, comment="SIZE")
    width = Column(String(100), nullable=True, comment="宽")
    height = Column(String(190), nullable=True, comment="高")
