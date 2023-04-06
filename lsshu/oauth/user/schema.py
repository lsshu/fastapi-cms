from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from lsshu.internal.schema import Schemas, SchemasPaginate
from lsshu.oauth.permission.schema import SchemasOAuthPermissionResponse
from lsshu.oauth.role.schema import SchemasOAuthRoleResponse


class SchemasOAuthRole(BaseModel):
    """角色 返回"""
    id: int
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasOAuthUserResponse(BaseModel):
    """授权用户 返回"""
    id: int
    username: Optional[str] = None
    user_phone: Optional[str] = None
    permissions: Optional[List[SchemasOAuthPermissionResponse]] = None
    roles: Optional[List[SchemasOAuthRole]] = None
    available: Optional[bool] = True
    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态
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


class SchemasOAuthUserBriefly(BaseModel):
    """授权用户简要 返回"""
    username: Optional[str] = None
    user_phone: Optional[str] = None
    available: Optional[bool] = True

    class Config:
        orm_mode = True


class SchemasOAuthUserAndScopes(BaseModel):
    """获取授权返回"""
    user: Optional[SchemasOAuthUserBriefly] = None
    scopes: Optional[list] = None


class SchemasOAuthUserMeStatusResponse(Schemas):
    """登录授权用户 状态返回"""
    data: SchemasOAuthUserAndScopes


class SchemasOAuthUserStoreUpdate(BaseModel):
    """授权用户 提交"""
    username: Optional[str] = None
    password: Optional[str] = None
    user_phone: Optional[str] = None
    available: Optional[bool] = True
    permissions: Optional[List[int]] = None
    roles: Optional[List[int]] = None

    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态


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
    roles: List[SchemasOAuthRole]
    permissions: List[SchemasOAuthPermissionResponse]


class SchemasOAuthUserMeUpdate(BaseModel):
    """授权用户修改自己信息 提交"""
    username: Optional[str] = None
    password: Optional[str] = None
    user_phone: Optional[str] = None



