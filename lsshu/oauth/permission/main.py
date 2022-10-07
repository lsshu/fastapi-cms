from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from config import OAUTH_DEFAULT_TAGS
from lsshu.internal.db import dbs
from lsshu.internal.depends import model_screen_params, model_post_screen_params, auth_user
from lsshu.internal.schema import ModelScreenParams, Schemas, SchemasError
from lsshu.oauth.model import permission_name
from lsshu.oauth.permission.crud import CRUDOAuthPermission
from lsshu.oauth.permission.schema import SchemasOAuthPermissionPaginateItem, SchemasOAuthPermissionTreeStatusResponse, SchemasOAuthPermissionResponse, \
    SchemasOAuthPermissionStoreUpdate, SchemasOAuthPermissionMenuStatusResponse, SchemasOAuthPermissionTreeResponse, SchemasOAuthPermissionMenu
from lsshu.oauth.user.schema import SchemasOAuthScopes

tags = OAUTH_DEFAULT_TAGS + ['Permission']
router = APIRouter(tags=tags)
permission_scopes = [permission_name, ]


@router.get('/{}'.format(permission_name), name="get {}".format(permission_name))
async def get_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % permission_name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthPermission.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasOAuthPermissionPaginateItem(**db_model_list))


@router.post('/{}.post'.format(permission_name), name="post {}".format(permission_name))
async def post_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_post_screen_params),
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % permission_name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUDOAuthPermission.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasOAuthPermissionPaginateItem(**db_model_list))


@router.get('/{}.params'.format(permission_name), name="get {}".format(permission_name))
async def params_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % permission_name])):
    """
    :param db:
    :param auth:
    :return:
    """
    return Schemas(data={})


@router.get('/{}.tree'.format(permission_name), name="get {}".format(permission_name))
async def tree_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % permission_name])):
    """
    :param db:
    :param auth:
    :return:
    """

    def json_fields(node):
        return node.to_dict()

    db_model_list = CRUDOAuthPermission.get_tree(db=db, json=True, json_fields=json_fields)
    return SchemasOAuthPermissionTreeStatusResponse(data=db_model_list)


@router.post('/{}.tree.post'.format(permission_name), name="post {}".format(permission_name))
async def tree_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % permission_name])):
    """
    :param db:
    :param auth:
    :return:
    """

    def json_fields(node):
        return node.to_dict()

    db_model_list = CRUDOAuthPermission.get_tree(db=db, json=True, json_fields=json_fields)

    def _response(model: dict):
        children = model.get('children', None)
        if children:
            model['children'] = [_response(_model) for _model in children]
        return SchemasOAuthPermissionTreeResponse(**model).dict()

    db_list = [_response(db_model) for db_model in db_model_list]
    return Schemas(data=db_list)


@router.get('/{}.menus'.format(permission_name), name="get {}".format(permission_name))
async def menus_permission_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user)):
    """
    :param db:
    :param auth:
    :return:
    """

    def query_fun(nodes):
        return nodes.filter(getattr(CRUDOAuthPermission.params_model, 'is_menu').is_(True)).filter(getattr(CRUDOAuthPermission.params_model, 'scope').in_(auth.scopes))

    def json_fields(node):
        return SchemasOAuthPermissionMenu(**node.to_dict()).dict()
        # return node.to_dict()

    db_model_list = CRUDOAuthPermission.get_tree(db=db, json=True, json_fields=json_fields, query=query_fun)
    return Schemas(data=db_model_list)


@router.post('/{}.menus.post'.format(permission_name), name="post {}".format(permission_name))
async def menus_permission_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user)):
    """
    :param db:
    :param auth:
    :return:
    """

    def query_fun(nodes):
        return nodes.filter(getattr(CRUDOAuthPermission.params_model, 'is_menu').is_(True)).filter(getattr(CRUDOAuthPermission.params_model, 'scope').in_(auth.scopes))

    def json_fields(node):
        return SchemasOAuthPermissionMenu(**node.to_dict()).dict()
        # return node.to_dict()

    db_model_list = CRUDOAuthPermission.get_tree(db=db, json=True, json_fields=json_fields, query=query_fun)
    return Schemas(data=db_model_list)


@router.get('/{}/{{pk}}'.format(permission_name), name="get {}".format(permission_name))
async def get_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.get" % permission_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthPermission.first(db=db, pk=pk)
    if db_model is None:
        return SchemasError(message="Data Not Found")
    return Schemas(data=SchemasOAuthPermissionResponse(**db_model.to_dict()))


@router.post('/{}'.format(permission_name), name="get {}".format(permission_name))
async def store_model(item: SchemasOAuthPermissionStoreUpdate, db: Session = Depends(dbs),
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.store" % permission_name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthPermission.first(db=db, where=("name", item.name))
    if db_model is not None:
        return SchemasError(message="Data Already Registered")
    bool_model = CRUDOAuthPermission.store(db=db, item=item)
    return Schemas(data=SchemasOAuthPermissionResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(permission_name), name="update {}".format(permission_name))
async def update_put_model(pk: int, item: SchemasOAuthPermissionStoreUpdate, db: Session = Depends(dbs),
                           auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % permission_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthPermission.first(db=db, pk=pk)
    if db_model is None:
        return SchemasError(message="Data Not Found")
    bool_model = CRUDOAuthPermission.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasOAuthPermissionResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}".format(permission_name), name="update {}".format(permission_name))
async def update_patch_model(pk: int, item: SchemasOAuthPermissionStoreUpdate, db: Session = Depends(dbs),
                             auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % permission_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthPermission.first(db=db, pk=pk)
    if db_model is None:
        return SchemasError(message="Data Not Found")
    bool_model = CRUDOAuthPermission.update(db=db, pk=pk, item=item, exclude_unset=True)
    return Schemas(data=SchemasOAuthPermissionResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}/move_inside".format(permission_name), name="update {}".format(permission_name))
async def move_inside_permission_model(pk: int, inside_id: int, db: Session = Depends(dbs),
                                       auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % permission_name])):
    """
    移动到 inside_id 下
    :param pk:
    :param inside_id:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.move_inside(db=db, inside_id=inside_id, pk=pk)
    return Schemas(data=bool_model)


@router.patch("/{}/{{pk}}/move_after".format(permission_name), name="update {}".format(permission_name))
async def move_after_permission_model(pk: int, after_id: int, db: Session = Depends(dbs),
                                      auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % permission_name])):
    """
    移动到 after_id 后
    :param pk:
    :param after_id:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.move_after(db=db, after_id=after_id, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}/{{pk}}".format(permission_name), name="delete {}".format(permission_name))
async def delete_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.delete" % permission_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(permission_name), name="deletes {}".format(permission_name))
async def delete_models(pks: List[int], db: Session = Depends(dbs),
                                   auth: SchemasOAuthScopes = Security(auth_user, scopes=permission_scopes + ["%s.delete" % permission_name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthPermission.delete(db=db, pks=pks)
    return Schemas(data=bool_model)
