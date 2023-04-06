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
    items: Optional[list] = None  # 当前页的数据列表
    pages: Optional[int] = None  # 总页数
    total: Optional[int] = None  # 总条数
    limit: Optional[int] = None  # 页条数


class ModelScreenParams(BaseModel):
    """获取列表默认参数"""
    page: Optional[int] = 1
    limit: Optional[int] = 25
    where: Optional[Union[dict, list]] = []
    join: Optional[Union[dict, list]] = []
    order: Optional[list] = []


class ModelScreenParamsForAll(BaseModel):
    """获取列表默认参数"""
    where: Optional[Union[dict, list]] = []
    join: Optional[Union[dict, list]] = []
    order: Optional[list] = []
