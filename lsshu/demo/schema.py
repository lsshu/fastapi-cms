from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from lsshu.internal.schema import SchemasPaginate


class SchemasResponse(BaseModel):
    """模型 返回"""
    id: int
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasStoreUpdate(BaseModel):
    """模型 提交"""
    name: Optional[str] = None


class SchemasPaginateItem(SchemasPaginate):
    items: List[SchemasResponse]


class SchemasParams(BaseModel):
    pass
