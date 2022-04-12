from datetime import datetime
from typing import Optional, List

from fastapi import Depends, Security, HTTPException, APIRouter, status
from fastapi.security import SecurityScopes, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Table, Text, event
from sqlalchemy_mptt.mixins import BaseNestedSets

from config import OAUTH_TOKEN_URL, OAUTH_TOKEN_SCOPES, OAUTH_SECRET_KEY, OAUTH_ALGORITHM, OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES, OAUTH_OAUTH_ROUTER, \
    OAUTH_DEFAULT_TAGS, OAUTH_LOGIN_SCOPES, OAUTH_ADMIN_USERS

from .helpers import token_verify_password, token_payload, token_access_token
from .. import Schemas, CRUDTree, plural, SchemasPaginate
from ..db import dbs, Model

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH_TOKEN_URL, scopes=OAUTH_TOKEN_SCOPES)
tags = OAUTH_DEFAULT_TAGS
router = APIRouter(**OAUTH_OAUTH_ROUTER)
_name = __name__.capitalize()
user_name = plural("%s.user" % _name)
user_scopes = [user_name, ]
role_name = plural("%s.role" % _name)
role_scopes = [role_name, ]
permission_name = plural("%s.permission" % _name)
permission_scopes = [permission_name, ]
SYSTEM_PERMISSIONS = [
    {
        "name": "后台管理", "scope": _name, "children": [
            {"name": "授权用户", "scope": user_name},
            {"name": "用户角色", "scope": role_name},
            {"name": "权限管理", "scope": permission_name, "action": [{"name": "菜单", "scope": "menus"}, {"name": "树", "scope": "tree"}]}
        ]
    }
]


class SchemasLoginResponse(Schemas):
    """登录"""
    access_token: str
    token_type: str


class SchemasOAuthUser(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = 0
    exp: Optional[int] = 0
    scopes: List[str] = []


class SchemasOAuthPermissionResponse(BaseModel):
    """权限 返回"""
    id: int
    name: Optional[str] = None
    scope: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasOAuthRoleResponse(BaseModel):
    """角色 返回"""
    id: int
    name: Optional[str] = None
    permissions: Optional[List[SchemasOAuthPermissionResponse]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasOAuthUserStoreUpdate(BaseModel):
    """授权用户 提交"""
    username: Optional[str] = None
    password: Optional[str] = None
    available: Optional[bool] = True
    permissions: Optional[List[int]] = None
    roles: Optional[List[int]] = None


class SchemasOAuthUserResponse(BaseModel):
    """授权用户 返回"""
    id: int
    username: Optional[str] = None
    permissions: Optional[List[SchemasOAuthPermissionResponse]] = None
    roles: Optional[List[SchemasOAuthRoleResponse]] = None
    available: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasOAuthScopes(BaseModel):
    user: SchemasOAuthUserResponse
    scopes: List[str] = []


class SchemasOAuthUserMeResponse(BaseModel):
    """登录授权用户  返回"""
    username: Optional[str] = None
    available: Optional[bool] = True

    class Config:
        orm_mode = True


class SchemasOAuthUserMeStatusResponse(Schemas):
    """登录授权用户 状态返回"""
    data: SchemasOAuthUserMeResponse
    scopes: Optional[list] = None


class SchemasOAuthUserPaginateItem(SchemasPaginate):
    items: List[SchemasOAuthUserResponse]


class SchemasOAuthRoleStoreUpdate(BaseModel):
    """授权角色 提交"""
    name: Optional[str] = None
    scopes: Optional[str] = None
    permissions: Optional[List[int]] = None


class SchemasOAuthRolePaginateItem(SchemasPaginate):
    items: List[SchemasOAuthRoleResponse]


class SchemasOAuthPermissionStoreUpdate(BaseModel):
    """授权角色 提交"""
    name: Optional[str] = None
    icon: Optional[str] = None
    scope: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[int] = None
    is_menu: Optional[bool] = True
    is_action: Optional[bool] = True


class SchemasOAuthPermissionPaginateItem(SchemasPaginate):
    items: List[SchemasOAuthPermissionResponse]


class SchemasOAuthPermissionTreeStatusResponse(Schemas):
    """状态返回"""
    data: list


user_table_name = user_name.replace('.', '_')
permission_table_name = permission_name.replace('.', '_')
role_table_name = role_name.replace('.', '_')
_table_name = _name.replace('.', '_')


class ModelOAuthUsers(Model, BaseNestedSets):
    """登录用户"""
    __tablename__ = user_table_name
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(15), nullable=False, unique=True, index=True, comment="名称")
    password = Column(String(128), nullable=False, comment="密码")
    available = Column(Boolean, default=1, comment="是否有效")
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
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.now, comment="创建日期")
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新日期")
    deleted_at = Column(TIMESTAMP, nullable=True, comment="删除日期")

    def __repr__(self):
        return "<User (%s)(%s)>" % (self.id, self.username)


class ModelOAuthRoles(Model, BaseNestedSets):
    """角色"""
    __tablename__ = role_table_name
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(15), nullable=False, unique=True, comment="名称")
    permissions = relationship('ModelOAuthPermissions', backref='roles', lazy="joined", secondary=Table(
        "%s_role_has_permissions" % _table_name,
        Model.metadata,
        Column('per_id', Integer, ForeignKey("%s.id" % permission_table_name), primary_key=True, comment="权限"),
        Column('rol_id', Integer, ForeignKey("%s.id" % role_table_name), primary_key=True, comment="角色")
    ))
    scopes = Column(Text, nullable=False, comment="Scope")
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.now, comment="创建日期")
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新日期")
    deleted_at = Column(TIMESTAMP, nullable=True, comment="删除日期")

    def __repr__(self):
        return "<Role (%s)(%s)>" % (self.id, self.name)


class ModelOAuthPermissions(Model, BaseNestedSets):
    """ 权限 """
    __tablename__ = permission_table_name
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(15), nullable=False, comment="名称")
    icon = Column(String(20), nullable=True, comment="ICO")
    scope = Column(String(50), nullable=False, unique=True, comment="Scope")
    path = Column(String(50), nullable=False, comment="Path")
    is_menu = Column(Boolean, default=True, comment="是否为菜单")
    is_action = Column(Boolean, default=True, comment="是否为动作权限")
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.now, comment="创建日期")
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新日期")
    deleted_at = Column(TIMESTAMP, nullable=True, comment="删除日期")

    def __repr__(self):
        return "<Permission (%s)(%s)>" % (self.id, self.name)


@event.listens_for(ModelOAuthPermissions.scope, 'set')
def receive_before_insert(target, value: str, old_value, initiator):
    target.path = "/%s" % value.replace('.', '/').lower()


@event.listens_for(ModelOAuthPermissions.scope, 'modified')
def receive_before_insert(target, initiator):
    target.path = "/%s" % target.scope.replace('.', '/').lower()


class CRUDOAuthUser(CRUDTree):
    """用户表操作"""
    params_model = ModelOAuthUsers
    params_pseudo_deletion = True  # 伪删除
    params_relationship = {
        "permissions": ModelOAuthPermissions,
        "roles": ModelOAuthRoles,
    }

    @classmethod
    def store(cls, db: Session, item: BaseModel, **kwargs):
        from .helpers import token_get_password_hash
        if hasattr(item, "password") and item.password:
            item.password = token_get_password_hash(item.password)

        return super(CRUDOAuthUser, cls).store(db=db, item=item, **kwargs)

    @classmethod
    def update(cls, db: Session, pk: int, item: BaseModel, **kwargs):
        from .helpers import token_get_password_hash
        if hasattr(item, "password") and item.password:
            item.password = token_get_password_hash(item.password)
        else:
            if hasattr(item, "password"):
                delattr(item, "password")

        return super(CRUDOAuthUser, cls).update(db=db, pk=pk, item=item, **kwargs)


class CRUDOAuthRole(CRUDTree):
    """用户表操作"""
    params_model = ModelOAuthRoles
    params_pseudo_deletion = True  # 伪删除
    params_relationship = {
        "permissions": ModelOAuthPermissions
    }

    @classmethod
    def store(cls, db: Session, item: BaseModel, **kwargs):
        from .. import BaseCRUD
        _relation = BaseCRUD.all(db=db, model=ModelOAuthPermissions, where=("id", 'in_', item.permissions))
        item.scopes = " ".join([relation.scope for relation in _relation])
        return super(CRUDOAuthRole, cls).store(db=db, item=item, **kwargs)

    @classmethod
    def update(cls, db: Session, pk: int, item: BaseModel, **kwargs):
        from .. import BaseCRUD
        _relation = BaseCRUD.all(db=db, model=ModelOAuthPermissions, where=("id", 'in_', item.permissions))
        item.scopes = " ".join([relation.scope for relation in _relation])
        return super(CRUDOAuthRole, cls).update(db=db, pk=pk, item=item, **kwargs)


class CRUDOAuthPermission(CRUDTree):
    """用户表操作"""
    params_model = ModelOAuthPermissions
    params_pseudo_deletion = True  # 伪删除


def authenticate_user(db: Session, username: str, password: str):
    """
    验证用户信息
    :param db:
    :param username:
    :param password:
    :return:
    """
    user = CRUDOAuthUser.first(db=db, where=("username", username))
    if not user:
        # 用户不存在
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not token_verify_password(plain_password=password, hashed_password=user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user


def token_authenticate_access_token(db, username: str, password: str, scopes: list):
    """
    认证用户且生成用户token
    :param db:
    :param username:
    :param password:
    :param scopes:
    :return:
    """
    from datetime import timedelta
    user = authenticate_user(db=db, username=username, password=password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=int(OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES))
    scopes = scopes + [OAUTH_LOGIN_SCOPES]
    """处理用户拥有的权限"""
    # Todo user.roles user.permission
    # scopes = scopes + []
    if user.username in OAUTH_ADMIN_USERS:
        permissions = CRUDOAuthPermission.all(db=db)
        scopes = scopes + [permission.scope for permission in permissions]

    """处理用户拥有的权限"""
    # print(scopes)
    return token_access_token(
        data={"sub": user.username, "user_id": user.id, "scopes": scopes},
        key=OAUTH_SECRET_KEY,
        algorithm=OAUTH_ALGORITHM,
        expires_delta=access_token_expires
    )


async def current_user_security(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    """
    解析加密字段
    :param security_scopes:
    :param token:
    :return:
    """
    payload = token_payload(security_scopes, token, OAUTH_SECRET_KEY, OAUTH_ALGORITHM)
    """处理授权用户实时情况"""
    # Todo
    """处理授权用户实时情况"""
    return SchemasOAuthUser(**payload, username=payload['sub'])


async def auth_user(user: SchemasOAuthUser = Security(current_user_security, scopes=[OAUTH_LOGIN_SCOPES]),
                    db: Session = Depends(dbs)):
    """
    demo
    :param user:
    :param db:
    :return:
    """
    auth = CRUDOAuthUser.first(db=db, where=("username", user.username))
    return SchemasOAuthScopes(user=auth, scopes=user.scopes)


@router.post('/token', tags=tags)
async def login_for_access_token(db: Session = Depends(dbs), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    获取登录授权:
    - **form_data**: 登录数据
    """
    access_token = token_authenticate_access_token(
        db=db,
        username=form_data.username,
        password=form_data.password,
        scopes=form_data.scopes
    )
    return SchemasLoginResponse(access_token=access_token, token_type="bearer")


@router.get('/me', tags=tags)
async def get_login_access_me(auth: SchemasOAuthScopes = Security(auth_user)):
    """
    获取登录授权:
    """
    return SchemasOAuthUserMeStatusResponse(data=auth.user, scopes=auth.scopes)


@router.get('/{}'.format(user_name), name="get {}".format(user_name), tags=tags)
async def user_models(db: Session = Depends(dbs), page: Optional[int] = 1, limit: Optional[int] = 25,
                      username: Optional[str] = None,
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.list" % user_name])):
    """
    :param db:
    :param page:
    :param limit:
    :param username:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthUser.paginate(
        db=db, page=page, limit=limit, where=("username", "like", username))
    return Schemas(data=SchemasOAuthUserPaginateItem(**db_model_list))


@router.get('/{}/{{pk}}'.format(user_name), name="get {}".format(user_name), tags=tags)
async def get_user_model(pk: int, db: Session = Depends(dbs),
                         auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.get" % user_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthUser.first(db=db, where=(CRUDOAuthUser.params_pk, pk))
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{} not found".format(user_name.capitalize()))
    return Schemas(data=SchemasOAuthUserResponse(**db_model.to_dict()))


@router.post('/{}'.format(user_name), name="get {}".format(user_name), tags=tags)
async def store_user_model(item: SchemasOAuthUserStoreUpdate, db: Session = Depends(dbs),
                           auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.store" % user_name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthUser.first(db=db, where=("username", item.username))
    if db_model is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="{} already registered".format(user_name.capitalize()))
    bool_model = CRUDOAuthUser.store(db=db, item=item)
    return Schemas(data=SchemasOAuthUserResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(user_name), name="update {}".format(user_name), tags=tags)
async def update_user_model(pk: int, item: SchemasOAuthUserStoreUpdate, db: Session = Depends(dbs),
                            auth: SchemasOAuthScopes = Security(auth_user,
                                                                scopes=user_scopes + ["%s.update" % user_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthUser.first(db=db, where=(CRUDOAuthUser.pk, pk))
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{} not found".format(user_name.capitalize()))
    bool_model = CRUDOAuthUser.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasOAuthUserResponse(**bool_model.to_dict()))


@router.delete("/{}/{{pk}}".format(user_name), name="delete {}".format(user_name), tags=tags)
async def delete_model(pk: int, db: Session = Depends(dbs),
                       auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.delete" % user_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthUser.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(user_name), name="deletes {}".format(user_name), tags=tags)
async def delete_models(pks: List[int], db: Session = Depends(dbs),
                        auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.delete" % user_name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthUser.delete(db=db, pks=pks)
    return Schemas(data=bool_model)


"""
角色操作
"""


@router.get('/{}'.format(role_name), name="get {}".format(role_name), tags=tags)
async def role_models(db: Session = Depends(dbs), page: Optional[int] = 1, limit: Optional[int] = 25,
                      name: Optional[str] = None,
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % role_name])):
    """
    :param db:
    :param page:
    :param limit:
    :param name:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthRole.paginate(db=db, page=page, limit=limit, where=("name", "like", name))
    return Schemas(items=SchemasOAuthRolePaginateItem(**db_model_list))


@router.get('/{}/{{pk}}'.format(role_name), name="get {}".format(role_name), tags=tags)
async def get_role_model(pk: int, db: Session = Depends(dbs),
                         auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.get" % role_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthRole.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{} not found".format(role_name.capitalize()))
    return Schemas(data=SchemasOAuthRoleResponse(**db_model))


@router.post('/{}'.format(role_name), name="get {}".format(role_name), tags=tags)
async def store_role_model(item: SchemasOAuthRoleStoreUpdate, db: Session = Depends(dbs),
                           auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.store" % role_name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthRole.first(db=db, where=("name", item.name))
    if db_model is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="{} already registered".format(role_name.capitalize()))
    bool_model = CRUDOAuthRole.store(db=db, item=item)
    return Schemas(data=SchemasOAuthRoleResponse(**bool_model.to_dict))


@router.put("/{}/{{pk}}".format(role_name), name="update {}".format(role_name), tags=tags)
async def update_role_model(pk: int, item: SchemasOAuthRoleStoreUpdate, db: Session = Depends(dbs),
                            auth: SchemasOAuthScopes = Security(auth_user,
                                                                scopes=role_scopes + ["%s.update" % role_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthRole.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{} not found".format(role_name.capitalize()))
    bool_model = CRUDOAuthRole.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasOAuthRoleResponse(**bool_model.to_dict))


@router.delete("/{}/{{pk}}".format(role_name), name="delete {}".format(role_name), tags=tags)
async def delete_role_model(pk: int, db: Session = Depends(dbs),
                            auth: SchemasOAuthScopes = Security(auth_user,
                                                                scopes=role_scopes + ["%s.delete" % role_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthRole.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(role_name), name="deletes {}".format(role_name), tags=tags)
async def delete_role_models(pks: List[int], db: Session = Depends(dbs),
                             auth: SchemasOAuthScopes = Security(auth_user,
                                                                 scopes=role_scopes + ["%s.delete" % role_name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthRole.delete(db=db, pks=pks)
    return Schemas(data=bool_model)


"""
权限操作
"""


@router.get('/{}'.format(permission_name), name="get {}".format(permission_name), tags=tags)
async def permission_models(db: Session = Depends(dbs), page: Optional[int] = 1, limit: Optional[int] = 25,
                            name: Optional[str] = None,
                            auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                "%s.list" % permission_name])):
    """
    :param db:
    :param page:
    :param limit:
    :param name:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthPermission.paginate(db=db, page=page, limit=limit, where=("name", "like", name))
    return Schemas(data=SchemasOAuthPermissionPaginateItem(**db_model_list))


@router.get('/{}.tree'.format(permission_name), name="get {}".format(permission_name), tags=tags)
async def tree_permission_models(db: Session = Depends(dbs),
                                 auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                     "%s.list" % permission_name])):
    """
    :param db:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthPermission.get_tree(db=db, json=True)
    return SchemasOAuthPermissionTreeStatusResponse(data=db_model_list)


@router.get('/{}.menus'.format(permission_name), name="get {}".format(permission_name), tags=tags)
async def menus_permission_models(db: Session = Depends(dbs),
                                  auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                      "%s.list" % permission_name])):
    """
    :param db:
    :param auth:
    :return:
    """

    def query_fun(nodes):
        return nodes.filter(getattr(CRUDOAuthPermission.params_model, CRUDOAuthPermission.params_delete_tag).is_(None)).filter(
            getattr(CRUDOAuthPermission.params_model, 'is_menu').is_(True))

    db_model_list = CRUDOAuthPermission.get_tree(db=db, json=True, query=query_fun)
    return SchemasOAuthPermissionTreeStatusResponse(data=db_model_list)


@router.get('/{}/{{pk}}'.format(permission_name), name="get {}".format(permission_name), tags=tags)
async def get_permission_model(pk: int, db: Session = Depends(dbs),
                               auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                   "%s.get" % permission_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthPermission.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="{} not found".format(permission_name.capitalize()))
    return Schemas(data=SchemasOAuthPermissionResponse(**db_model.to_dict))


@router.post('/{}'.format(permission_name), name="get {}".format(permission_name), tags=tags)
async def store_permission_model(item: SchemasOAuthPermissionStoreUpdate, db: Session = Depends(dbs),
                                 auth: SchemasOAuthScopes = Security(auth_user,
                                                                     scopes=permission_scopes + [
                                                                         "%s.store" % permission_name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthPermission.first(db=db, where=("name", item.name))
    if db_model is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="{} already registered".format(permission_name.capitalize()))
    bool_model = CRUDOAuthPermission.store(db=db, item=item)
    return Schemas(data=SchemasOAuthPermissionResponse(**bool_model.to_dict))


@router.put("/{}/{{pk}}".format(permission_name), name="update {}".format(permission_name), tags=tags)
async def update_permission_model(pk: int, item: SchemasOAuthPermissionStoreUpdate, db: Session = Depends(dbs),
                                  auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                      "%s.update" % permission_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthPermission.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="{} not found".format(permission_name.capitalize()))
    bool_model = CRUDOAuthPermission.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasOAuthPermissionResponse(**bool_model.to_dict))


@router.patch("/{}/{{pk}}/move_inside".format(permission_name), name="update {}".format(permission_name), tags=tags)
async def move_inside_permission_model(pk: int, inside_id: int, db: Session = Depends(dbs),
                                       auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                           "%s.update" % permission_name])):
    """
    移动到 inside_id 下
    :param pk:
    :param inside_id:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.move_inside(db=db, inside_id=inside_id, pk=pk)
    return Schemas(data=bool_model)


@router.patch("/{}/{{pk}}/move_after".format(permission_name), name="update {}".format(permission_name), tags=tags)
async def move_after_permission_model(pk: int, after_id: int, db: Session = Depends(dbs),
                                      auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                          "%s.update" % permission_name])):
    """
    移动到 after_id 后
    :param pk:
    :param after_id:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.move_after(db=db, after_id=after_id, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}/{{pk}}".format(permission_name), name="delete {}".format(permission_name), tags=tags)
async def delete_permission_model(pk: int, db: Session = Depends(dbs),
                                  auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                      "%s.delete" % permission_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(permission_name), name="deletes {}".format(permission_name), tags=tags)
async def delete_permission_models(pks: List[int], db: Session = Depends(dbs),
                                   auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + [
                                       "%s.delete" % permission_name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.delete(db=db, pks=pks)
    return Schemas(data=bool_model)
