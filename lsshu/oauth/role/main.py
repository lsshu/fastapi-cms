from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from config import OAUTH_DEFAULT_TAGS
from lsshu.internal.db import dbs
from lsshu.internal.depends import model_screen_params, model_post_screen_params, auth_user
from lsshu.internal.schema import ModelScreenParams, Schemas, SchemasError
from lsshu.oauth.model import role_name
from lsshu.oauth.permission.crud import CRUDOAuthPermission
from lsshu.oauth.role.crud import CRUDOAuthRole
from lsshu.oauth.role.schema import SchemasOAuthRolePaginateItem, SchemasParams, SchemasOAuthRoleResponse, SchemasOAuthRoleStoreUpdate
from lsshu.oauth.user.schema import SchemasOAuthScopes

tags = OAUTH_DEFAULT_TAGS + ['Role']
router = APIRouter(tags=tags)
role_scopes = [role_name, ]


@router.get('/{}'.format(role_name), name="get {}".format(role_name))
async def get_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % role_name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthRole.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasOAuthRolePaginateItem(**db_model_list))


@router.post('/{}.post'.format(role_name), name="post {}".format(role_name))
async def post_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_post_screen_params),
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % role_name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthRole.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasOAuthRolePaginateItem(**db_model_list))


@router.get('/{}.params'.format(role_name), name="get {}".format(role_name))
async def params_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % role_name])):
    """
    :param db:
    :param auth:
    :return:
    """

    def json_fields(node):
        return node.to_dict()

    data = {
        "permissions": CRUDOAuthPermission.get_tree(db=db, json=True, json_fields=json_fields)
    }
    return Schemas(data=SchemasParams(**data))


@router.get('/{}/{{pk}}'.format(role_name), name="get {}".format(role_name))
async def get_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.get" % role_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthRole.first(db=db, pk=pk)
    if db_model is None:
        return SchemasError(message="Data Not Found")
    return Schemas(data=SchemasOAuthRoleResponse(**db_model))


@router.post('/{}'.format(role_name), name="get {}".format(role_name))
async def store_model(item: SchemasOAuthRoleStoreUpdate, db: Session = Depends(dbs),
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.store" % role_name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthRole.first(db=db, where=("name", item.name))
    if db_model is not None:
        return SchemasError(message="Data Already Registered")
    bool_model = CRUDOAuthRole.store(db=db, item=item)
    return Schemas(data=SchemasOAuthRoleResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(role_name), name="update {}".format(role_name))
async def update_put_model(pk: int, item: SchemasOAuthRoleStoreUpdate, db: Session = Depends(dbs),
                           auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.update" % role_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthRole.first(db=db, pk=pk)
    if db_model is None:
        return SchemasError(message="Data Not Found")
    bool_model = CRUDOAuthRole.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasOAuthRoleResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}".format(role_name), name="update {}".format(role_name))
async def update_patch_model(pk: int, item: SchemasOAuthRoleStoreUpdate, db: Session = Depends(dbs),
                             auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.update" % role_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthRole.first(db=db, pk=pk)
    if db_model is None:
        return SchemasError(message="Data Not Found")
    bool_model = CRUDOAuthRole.update(db=db, pk=pk, item=item, exclude_unset=True)
    return Schemas(data=SchemasOAuthRoleResponse(**bool_model.to_dict()))


@router.delete("/{}/{{pk}}".format(role_name), name="delete {}".format(role_name))
async def delete_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.delete" % role_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthRole.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(role_name), name="deletes {}".format(role_name))
async def delete_models(pks: List[int], db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=role_scopes + ["%s.delete" % role_name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthRole.delete(db=db, pks=pks)
    return Schemas(data=bool_model)
