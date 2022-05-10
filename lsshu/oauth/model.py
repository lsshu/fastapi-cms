from sqlalchemy import Column, Integer, ForeignKey, Table, event
from sqlalchemy.orm import relationship

from lsshu.internal.method import plural
from lsshu.internal.model import Model, Engine, _ModelOAuthUsers, _ModelOAuthRoles, _ModelOAuthPermissions

_name = __name__.capitalize()
_table_name = _name.replace('.', '_')
user_name = plural("%s.user" % _name)
role_name = plural("%s.role" % _name)
permission_name = plural("%s.permission" % _name)

user_table_name = user_name.replace('.', '_')
permission_table_name = permission_name.replace('.', '_')
role_table_name = role_name.replace('.', '_')

SYSTEM_PERMISSIONS = [
    {
        "name": "后台管理", "scope": _name, "children": [
        {"name": "授权用户", "scope": user_name},
        {"name": "用户角色", "scope": role_name},
        {"name": "权限管理", "scope": permission_name, "action": [{"name": "菜单", "scope": "menus"}, {"name": "树", "scope": "tree"}]}
    ]
    }
]


class ModelOAuthUsers(_ModelOAuthUsers):
    """登录用户"""
    __tablename__ = user_table_name
    permissions = relationship('ModelOAuthPermissions', backref='auth_users', secondary=Table(
        "%s_user_has_permissions" % _table_name,
        Model.metadata,
        Column('per_id', Integer, ForeignKey("%s.id" % permission_table_name), primary_key=True, comment="权限"),
        Column('use_id', Integer, ForeignKey("%s.id" % user_table_name), primary_key=True, comment="用户"),
    ))
    roles = relationship('ModelOAuthRoles', backref='auth_users', secondary=Table(
        "%s_user_has_roles" % _table_name,
        Model.metadata,
        Column('rol_id', Integer, ForeignKey("%s.id" % role_table_name), primary_key=True, comment="角色"),
        Column('use_id', Integer, ForeignKey("%s.id" % user_table_name), primary_key=True, comment="用户"),
    ))


class ModelOAuthRoles(_ModelOAuthRoles):
    """角色"""
    __tablename__ = role_table_name
    permissions = relationship('ModelOAuthPermissions', backref='roles', lazy="joined", secondary=Table(
        "%s_role_has_permissions" % _table_name,
        Model.metadata,
        Column('per_id', Integer, ForeignKey("%s.id" % permission_table_name), primary_key=True, comment="权限"),
        Column('rol_id', Integer, ForeignKey("%s.id" % role_table_name), primary_key=True, comment="角色")
    ))


class ModelOAuthPermissions(_ModelOAuthPermissions):
    """ 权限 """
    __tablename__ = permission_table_name


@event.listens_for(ModelOAuthPermissions.scope, 'set')
def receive_before_insert(target, value: str, old_value, initiator):
    target.path = "/%s" % value.replace('.', '/').lower()


@event.listens_for(ModelOAuthPermissions.scope, 'modified')
def receive_before_insert(target, initiator):
    target.path = "/%s" % target.scope.replace('.', '/').lower()