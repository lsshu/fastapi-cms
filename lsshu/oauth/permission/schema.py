from datetime import datetime
from typing import Optional, Union, List

from pydantic import BaseModel

from lsshu.internal.schema import SchemasPaginate, Schemas


class SchemasOAuthPermissionResponse(BaseModel):
    """权限 返回"""
    id: int
    name: Optional[str] = None
    icon: Optional[str] = None
    scope: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[int] = None
    is_menu: Optional[bool] = True
    is_action: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasOAuthPermissionThinResponse(BaseModel):
    """权限 返回"""
    id: int
    name: Optional[str] = None

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


class SchemasOAuthPermissionTreeResponse(SchemasOAuthPermissionResponse):
    """权限 返回"""
    children: Optional[list] = None


class SchemasOAuthPermissionTreeStatusResponse(Schemas):
    """状态树返回"""
    data: List[SchemasOAuthPermissionTreeResponse]


class SchemasOAuthPermissionMenu(BaseModel):
    """权限 返回"""
    id: int
    name: Optional[str] = None
    icon: Optional[str] = None
    scope: Optional[str] = None
    path: Optional[str] = None

    class Config:
        orm_mode = True


class SchemasOAuthPermissionMenuResponse(SchemasOAuthPermissionMenu):
    """菜单 返回"""
    children: Optional[List[SchemasOAuthPermissionMenu]] = None


class SchemasOAuthPermissionMenuStatusResponse(Schemas):
    """菜单树返回"""
    data: List[SchemasOAuthPermissionMenuResponse]
