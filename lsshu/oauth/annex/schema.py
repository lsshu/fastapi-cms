from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from lsshu.internal.schema import SchemasPaginate


class SchemasResponse(BaseModel):
    """模型 返回"""
    md5: Optional[str] = None
    path: Optional[str] = None
    preview_path: Optional[str] = None
    size: Optional[int] = None

    class Config:
        orm_mode = True


class SchemasStoreUpdate(BaseModel):
    """模型 提交"""
    filename: Optional[str] = None
    content_type: Optional[str] = None
    md5: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None



class SchemasPaginateItem(SchemasPaginate):
    items: List[SchemasResponse]


class SchemasParams(BaseModel):
    pass
