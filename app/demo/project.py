"""
XX操作
"""
from datetime import datetime
from typing import Optional, List

from fastapi import Security, Depends, APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import Session

from lsshu import BaseCRUD, Schemas, SchemasPaginate, plural
from lsshu.db import dbs, Model
from lsshu.oauth import SchemasOAuthScopes, auth_user

name = plural(__name__.capitalize())
scopes = [name, ]
tags = [name, ]
permission = {"name": "project", "scope": name, "action": [{"name": "pro", "scope": "pro"}]}


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


table_name = name.replace('.', '_')


class Models(Model):
    """ 模型 """
    __tablename__ = table_name
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(15), nullable=False, unique=True, comment="名称")
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.now, comment="创建日期")
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新日期")
    deleted_at = Column(TIMESTAMP, nullable=True, comment="删除日期")


class CRUD(BaseCRUD):
    """表操作"""
    params_model = Models
    params_pseudo_deletion = True  # 伪删除


router = APIRouter()


@router.get('/{}'.format(name), name="get {}".format(name), tags=tags)
async def models(db: Session = Depends(dbs), page: Optional[int] = 1, limit: Optional[int] = 25,
                 name: Optional[str] = None, auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes)):
    """
    :param db:
    :param page:
    :param limit:
    :param name:
    :param auth:
    :return:
    """
    db_list = CRUD.paginate(db=db, page=page, limit=limit, where=("name", "like", name))
    return Schemas(data=SchemasPaginateItem(**db_list))


@router.get('/{}/{{pk}}'.format(name), name="get {}".format(name), tags=tags)
async def get_model(pk: int, db: Session = Depends(dbs),
                    auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes)):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="{} not found".format(name.capitalize()))
    return Schemas(data=SchemasResponse(**db_model.to_dict()))


@router.post('/{}'.format(name), name="get {}".format(name), tags=tags)
async def store_model(item: SchemasStoreUpdate, db: Session = Depends(dbs),
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.store" % name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, where=("name", item.name))
    if db_model is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="{} already registered".format(name.capitalize()))
    bool_model = CRUD.store(db=db, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(name), name="update {}".format(name), tags=tags)
async def update_model(pk: int, item: SchemasStoreUpdate, db: Session = Depends(dbs),
                       auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.update" % name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="{} not found".format(name.capitalize()))
    bool_model = CRUD.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.delete("/{}/{{pk}}".format(name), name="delete {}".format(name), tags=tags)
async def delete_model(pk: int, db: Session = Depends(dbs),
                       auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(name), name="deletes {}".format(name), tags=tags)
async def delete_models(pks: List[int], db: Session = Depends(dbs),
                        auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pks=pks)
    return Schemas(data=bool_model)
