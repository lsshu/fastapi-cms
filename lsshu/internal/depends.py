from typing import Optional, Union

from fastapi import Depends, Security
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import OAUTH_TOKEN_URL, OAUTH_TOKEN_SCOPES, OAUTH_SECRET_KEY, OAUTH_ALGORITHM, OAUTH_LOGIN_SCOPES
from lsshu.internal.db import dbs
from lsshu.internal.helpers import token_payload
from lsshu.internal.schema import ModelScreenParams
from lsshu.oauth.user.crud import CRUDOAuthUser
from lsshu.oauth.user.schema import SchemasOAuthUser, SchemasOAuthScopes


def model_screen_params(page: Optional[int] = 1, limit: Optional[int] = 25, where: Optional[Union[dict, list]] = None):
    """列表筛选参数"""
    return ModelScreenParams(page=page, limit=limit, where=where)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH_TOKEN_URL, scopes=OAUTH_TOKEN_SCOPES)


async def current_user_security(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    """
    解析加密字段
    :param security_scopes:
    :param token:
    :return:
    """
    payload = token_payload(security_scopes, token, OAUTH_SECRET_KEY, OAUTH_ALGORITHM)
    """处理授权用户实时情况"""
    # Todo
    """处理授权用户实时情况"""
    return SchemasOAuthUser(**payload)


async def auth_user(auth: SchemasOAuthUser = Security(current_user_security, scopes=[OAUTH_LOGIN_SCOPES]),
                    db: Session = Depends(dbs)):
    """
    demo
    :param auth:
    :param db:
    :return:
    """
    user = CRUDOAuthUser.first(db=db, pk=auth.user_id)
    return SchemasOAuthScopes(user=user, scopes=auth.scopes)
