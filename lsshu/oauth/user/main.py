from typing import List, Optional

from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import OAUTH_DEFAULT_TAGS, OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES, OAUTH_LOGIN_SCOPES, OAUTH_ADMIN_USERS, OAUTH_SECRET_KEY, OAUTH_ALGORITHM, \
    OAUTH_TOKEN_URI, OAUTH_SCOPES_URI, OAUTH_ME_URI
from lsshu.internal.db import dbs
from lsshu.internal.depends import model_screen_params, model_post_screen_params, auth_user
from lsshu.internal.helpers import token_access_token, token_verify_password
from lsshu.internal.schema import Schemas, SchemasError, ModelScreenParams
from lsshu.oauth.model import user_name
from lsshu.oauth.permission.crud import CRUDOAuthPermission
from lsshu.oauth.role.crud import CRUDOAuthRole
from lsshu.oauth.user.crud import CRUDOAuthUser
from lsshu.oauth.user.schema import SchemasOAuthScopes, SchemasLoginResponse, SchemasLogin, SchemasOAuthUserMeStatusResponse, SchemasPaginateItem, SchemasParams, \
    SchemasOAuthUserResponse, SchemasOAuthUserStoreUpdate, SchemasOAuthUserMeUpdate

tags = OAUTH_DEFAULT_TAGS + ['User']
router = APIRouter(tags=tags)
user_scopes = [user_name, ]


def authenticate_user(db: Session, username: str, password: str):
    """
    验证用户信息
    :param db:
    :param username:
    :param password:
    :return:
    """
    from lsshu.oauth.user.crud import CRUDOAuthUser
    user = CRUDOAuthUser.first(db=db, where=("username", username))

    if not user or not token_verify_password(plain_password=password, hashed_password=user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    return user


def token_authenticate_access_token(db, username: str, password: str, scopes: list) -> str:
    """
    认证用户且生成用户token
    :param db:
    :param username:
    :param password:
    :param scopes:
    :return:
    """
    from datetime import timedelta
    user = authenticate_user(db=db, username=username, password=password)
    access_token_expires = timedelta(minutes=int(OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES))
    scopes = scopes + [OAUTH_LOGIN_SCOPES]
    """处理用户拥有的权限"""
    # Todo user.roles user.permission
    if user.username in OAUTH_ADMIN_USERS:
        from lsshu.oauth.permission.crud import CRUDOAuthPermission
        permissions = CRUDOAuthPermission.all(db=db)
        scopes = scopes + [permission.scope for permission in permissions]
    else:
        # 获取用户权限
        scopes = scopes + [permission.scope for permission in user.permissions]
        # 获取用户角色权限
        scopes = scopes + [scope for role in user.roles for scope in (role.scopes.split(' '))]
    """处理用户拥有的权限"""
    return token_access_token(
        data={"sub": user.username, "user_id": user.id, "scopes": list(set(scopes))},
        key=OAUTH_SECRET_KEY,
        algorithm=OAUTH_ALGORITHM,
        expires_delta=access_token_expires
    )


from fastapi.param_functions import Form


class _OAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
            self,
            grant_type: str = Form(default=None, regex="password"),
            username: str = Form(),
            password: str = Form(),
            scope: str = Form(default=""),
            client_id: Optional[str] = Form(default=None),
            client_secret: Optional[str] = Form(default=None),
            verification_username: Optional[str] = Form(default=None),
            verification_code: Optional[str] = Form(default=None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
        self.verification_username = verification_username
        self.verification_code = verification_code


@router.post(OAUTH_TOKEN_URI)
async def login_for_access_token(db: Session = Depends(dbs), form_data: _OAuth2PasswordRequestForm = Depends()):
    """
    获取登录授权:
    - **form_data**: 登录数据
    """
    access_token = token_authenticate_access_token(
        db=db,
        username=form_data.username,
        password=form_data.password,
        scopes=form_data.scopes
    )
    return SchemasLoginResponse(data=SchemasLogin(access_token=access_token, token_type="bearer"))



@router.get(OAUTH_SCOPES_URI)
async def get_scopes(auth: SchemasOAuthScopes = Security(auth_user)):
    """
    获取登录授权:
    """
    return SchemasOAuthUserMeStatusResponse(data={"user": auth.user, "scopes": auth.scopes})


@router.get(OAUTH_ME_URI)
async def get_me(auth: SchemasOAuthScopes = Security(auth_user)):
    """
    获取登录授权的用户信息:
    """
    return Schemas(data=auth.user)


@router.patch(OAUTH_ME_URI)
async def patch_me(item: SchemasOAuthUserStoreUpdate, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user)):
    """
    更新登录授权用户的信息:
    """
    bool_model = CRUDOAuthUser.update(db=db, pk=auth.user.id, item=item)
    return Schemas(data=SchemasOAuthUserResponse(**bool_model.to_dict()))


@router.get('/{}'.format(user_name), name="get {}".format(user_name))
async def get_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.list" % user_name])):
    """
    获取授权用户列表
    - **:param db**:
    - **:param params**:
    - **:param auth**:
    - **:return**:
    """
    db_model_list = CRUDOAuthUser.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.post('/{}.post'.format(user_name), name="post {}".format(user_name))
async def post_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_post_screen_params),
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.list" % user_name])):
    """
    获取授权用户列表
    - **:param db**:
    - **:param params**:
    - **:param auth**:
    - **:return**:
    """
    db_model_list = CRUDOAuthUser.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.get('/{}.params'.format(user_name), name="get {}".format(user_name))
async def params_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.list" % user_name])):
    """
    :param db:
    :param auth:
    :return:
    """
    data = {
        "roles": CRUDOAuthRole.all(db=db),
        "permissions": CRUDOAuthPermission.all(db=db)
    }

    return Schemas(data=SchemasParams(**data))


@router.get('/{}/{{pk}}'.format(user_name), name="get {}".format(user_name))
async def get_model(pk: int, db: Session = Depends(dbs),
                    auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.get" % user_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthUser.first(db=db, where=(CRUDOAuthUser.params_pk, pk))
    if db_model is None:
        return SchemasError(message="Data Not Found")
    return Schemas(data=SchemasOAuthUserResponse(**db_model.to_dict()))


@router.post('/{}'.format(user_name), name="get {}".format(user_name))
async def store_model(item: SchemasOAuthUserStoreUpdate, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.store" % user_name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthUser.first(db=db, where=("username", item.username))
    if db_model is not None:
        return SchemasError(message="Data Already Registered")
    bool_model = CRUDOAuthUser.store(db=db, item=item)
    return Schemas(data=SchemasOAuthUserResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(user_name), name="update {}".format(user_name))
async def update_put_model(pk: int, item: SchemasOAuthUserStoreUpdate, db: Session = Depends(dbs),
                           auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.update" % user_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthUser.first(db=db, where=(CRUDOAuthUser.pk, pk))
    if db_model is None:
        return SchemasError(message="Data Not Found")
    bool_model = CRUDOAuthUser.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasOAuthUserResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}".format(user_name), name="update {}".format(user_name))
async def update_patch_model(pk: int, item: SchemasOAuthUserStoreUpdate, db: Session = Depends(dbs),
                             auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.update" % user_name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUDOAuthUser.first(db=db, where=(CRUDOAuthUser.pk, pk))
    if db_model is None:
        return SchemasError(message="Data Not Found")
    bool_model = CRUDOAuthUser.update(db=db, pk=pk, item=item, exclude_unset=True)
    return Schemas(data=SchemasOAuthUserResponse(**bool_model.to_dict()))


@router.delete("/{}/{{pk}}".format(user_name), name="delete {}".format(user_name))
async def delete_model(pk: int, db: Session = Depends(dbs),
                       auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.delete" % user_name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthUser.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(user_name), name="deletes {}".format(user_name))
async def delete_models(pks: List[int], db: Session = Depends(dbs),
                        auth: SchemasOAuthScopes = Security(auth_user, scopes=user_scopes + ["%s.delete" % user_name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUDOAuthUser.delete(db=db, pks=pks)
    return Schemas(data=bool_model)
