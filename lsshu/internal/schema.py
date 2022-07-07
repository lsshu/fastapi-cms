from typing import Optional, Union

from pydantic import BaseModel

from config import SCHEMAS_SUCCESS_CODE, SCHEMAS_SUCCESS_STATUS, SCHEMAS_SUCCESS_MESSAGE, SCHEMAS_ERROR_CODE, SCHEMAS_ERROR_STATUS, SCHEMAS_ERROR_MESSAGE


class Schemas(BaseModel):
    """状态返回"""
    code: Optional[int] = SCHEMAS_SUCCESS_CODE
    status: Optional[str] = SCHEMAS_SUCCESS_STATUS
    message: Optional[str] = SCHEMAS_SUCCESS_MESSAGE
    data: Optional[Union[BaseModel, dict, list, str, bool, None]] = None


class SchemasError(BaseModel):
    """状态返回"""
    code: Optional[int] = SCHEMAS_ERROR_CODE
    status: Optional[str] = SCHEMAS_ERROR_STATUS
    message: Optional[str] = SCHEMAS_ERROR_MESSAGE
    data: Optional[Union[BaseModel, dict, list, str, bool, None]] = None


class SchemasPaginate(BaseModel):
    """分页"""
    # has_next: bool  # 如果下一页存在，返回True
    # has_prev: bool  # 如果上一页存在，返回True
    items: list  # 当前页的数据列表
    # next_num: Union[int, None]  # 下一页的页码
    # prev_num: Union[int, None]  # 上一页的页码
    # page: Union[int, None]  # 当前页码
    pages: int  # 总页数
    # per_page: Union[int, None]  # 每页的条数
    total: int  # 总条数


class ModelScreenParams(BaseModel):
    """获取列表默认参数"""
    page: Optional[int] = 1
    limit: Optional[int] = 25
    where: Optional[Union[dict, list]] = None
    order: Optional[list] = None
