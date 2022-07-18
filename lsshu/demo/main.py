from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from lsshu.internal.db import dbs
from lsshu.internal.depends import model_screen_params, model_post_screen_params, auth_user
from lsshu.internal.schema import ModelScreenParams, Schemas, SchemasError
from lsshu.oauth.user.schema import SchemasOAuthScopes

from lsshu.demo.crud import CRUD
from lsshu.demo.model import name as name
from lsshu.demo.schema import SchemasResponse, SchemasParams, SchemasPaginateItem, SchemasStoreUpdate

router = APIRouter(tags=["Demo"])
scopes = [name, ]


@router.get('/{}'.format(name), name="get {}".format(name))
async def get_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.list" % name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUD.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.post('/{}.post'.format(name), name="get {}".format(name))
async def get_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_post_screen_params),
                     auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.list" % name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUD.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.get('/{}.params'.format(name), name="get {}".format(name))
async def params_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.list" % name])):
    """
    :param db:
    :param auth:
    :return:
    """

    data = {}
    return Schemas(data=SchemasParams(**data))


@router.get('/{}/{{pk}}'.format(name), name="get {}".format(name))
async def get_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.get" % name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, pk=pk)
    if db_model is None:
        return SchemasError(message="Data Not Found")
    return Schemas(data=SchemasResponse(**db_model.to_dict()))


@router.post('/{}'.format(name), name="get {}".format(name))
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
        return SchemasError(message="Data Already Registered")
    bool_model = CRUD.store(db=db, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(name), name="update {}".format(name))
async def update_put_model(pk: int, item: SchemasStoreUpdate, db: Session = Depends(dbs),
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
        return SchemasError(message="Data Not Found")
    bool_model = CRUD.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}".format(name), name="update {}".format(name))
async def update_patch_model(pk: int, item: SchemasStoreUpdate, db: Session = Depends(dbs),
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
        return SchemasError(message="Data Not Found")
    bool_model = CRUD.update(db=db, pk=pk, item=item, exclude_unset=True)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.delete("/{}/{{pk}}".format(name), name="delete {}".format(name))
async def delete_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(name), name="deletes {}".format(name))
async def delete_models(pks: List[int], db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pks=pks)
    return Schemas(data=bool_model)
