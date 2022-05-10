from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy_mptt.mixins import BaseNestedSets

from lsshu.internal.db import Model, Engine


class _ModelOAuthUsers(Model, BaseNestedSets):
    """登录用户"""
    __abstract__ = True
    username = Column(String(15), nullable=False, unique=True, index=True, comment="名称")
    password = Column(String(128), nullable=False, comment="密码")
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
