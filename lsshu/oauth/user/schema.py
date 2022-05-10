from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from lsshu.internal.schema import Schemas, SchemasPaginate
from lsshu.oauth.permission.schema import SchemasOAuthPermissionResponse
from lsshu.oauth.role.schema import SchemasOAuthRoleResponse


class SchemasOAuthUserResponse(BaseModel):
    """授权用户 返回"""
    id: int
    username: Optional[str] = None
    permissions: Optional[List[SchemasOAuthPermissionResponse]] = None
    roles: Optional[List[SchemasOAuthRoleResponse]] = None
    stores: Optional[list] = None
    available: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasPaginateItem(SchemasPaginate):
    items: List[SchemasOAuthUserResponse]


class SchemasLogin(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None


class SchemasLoginResponse(Schemas):
    """登录"""
    data = SchemasLogin


class SchemasOAuthUserMeStatusResponse(Schemas):
    """登录授权用户 状态返回"""
    data: SchemasOAuthUserResponse
    scopes: Optional[list] = None


class SchemasOAuthUserStoreUpdate(BaseModel):
    """授权用户 提交"""
    username: Optional[str] = None
    password: Optional[str] = None
    available: Optional[bool] = True
    permissions: Optional[List[int]] = None
    roles: Optional[List[int]] = None
    stores: Optional[List[int]] = None


class SchemasOAuthUser(BaseModel):
    """解析加密字段"""
    sub: Optional[str] = None
    user_id: Optional[int] = 0
    exp: Optional[int] = 0
    scopes: List[str] = []


class SchemasOAuthScopes(BaseModel):
    """验证授权后"""
    user: SchemasOAuthUserResponse
    scopes: List[str] = []


class SchemasParams(BaseModel):
    """参数"""
    roles: List[SchemasOAuthRoleResponse]
    permissions: List[SchemasOAuthPermissionResponse]