from datetime import datetime
from typing import Optional, Union, List

from pydantic import BaseModel

from lsshu.internal.schema import SchemasPaginate, Schemas


class SchemasOAuthPermissionResponse(BaseModel):
    """权限 返回"""
    id: int
    name: Optional[str] = None
    scope: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasOAuthPermissionPaginateItem(SchemasPaginate):
    items: List[SchemasOAuthPermissionResponse]


class SchemasOAuthPermissionStoreUpdate(BaseModel):
    """授权角色 提交"""
    name: Optional[str] = None
    icon: Optional[str] = None
    scope: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[int] = None
    is_menu: Optional[bool] = True
    is_action: Optional[bool] = True


class SchemasOAuthPermissionTreeStatusResponse(Schemas):
    """状态返回"""
    data: list
