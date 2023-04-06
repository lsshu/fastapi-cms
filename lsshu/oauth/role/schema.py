from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from lsshu.internal.schema import SchemasPaginate
from lsshu.oauth.permission.schema import SchemasOAuthPermissionThinResponse


class SchemasOAuthRoleResponse(BaseModel):
    """角色 返回"""
    id: int
    name: Optional[str] = None
    permissions: Optional[List[SchemasOAuthPermissionThinResponse]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasOAuthRolePaginateItem(SchemasPaginate):
    items: List[SchemasOAuthRoleResponse]


class SchemasOAuthRoleStoreUpdate(BaseModel):
    """授权角色 提交"""
    name: Optional[str] = None
    scopes: Optional[str] = None
    permissions: Optional[List[int]] = None


class SchemasParams(BaseModel):
    permissions: Optional[list] = None
