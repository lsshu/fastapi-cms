import json
from typing import Optional

from fastapi import Depends, Security
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import OAUTH_TOKEN_URL, OAUTH_TOKEN_SCOPES, OAUTH_SECRET_KEY, OAUTH_ALGORITHM, OAUTH_LOGIN_SCOPES
from lsshu.internal.db import dbs
from lsshu.internal.helpers import token_payload
from lsshu.internal.schema import ModelScreenParams, ModelScreenParamsForAll
from lsshu.oauth.user.crud import CRUDOAuthUser
from lsshu.oauth.user.schema import SchemasOAuthUser, SchemasOAuthScopes


def model_screen_params(page: Optional[int] = 1, limit: Optional[int] = 25, quest_data: Optional[str] = None):
    """列表筛选参数"""
    order, where = [], []
    if bool(quest_data):
        quest_data = json.loads(quest_data) if quest_data else None
        [order.extend(list(s.items())) for s in quest_data['sort']] if 'sort' in quest_data else None
        where = [(w['key'], w['condition'], w['value']) for w in quest_data['where']] if 'where' in quest_data else None
    return ModelScreenParams(page=page, limit=limit, order=order, where=where)


def model_post_screen_params(data: ModelScreenParams = None):
    """列表筛选参数"""
    order = []
    [order.extend(list(s.items())) for s in data.order]
    data.order = order
    where = [(w['key'], w['condition'], w['value']) for w in data.where if
             ('value' in w and (w['value'] or w['value'] is False or w['value'] == 0)) and (not "join" in w or "join" in w and not w['join'])]
    join = [(w['join'], [(w['key'], w['condition'], w['value'])], 'join') for w in data.where if
            ('value' in w and (w['value'] or w['value'] is False or w['value'] == 0)) and ("join" in w and w['join'])]
    data.where = where
    data.join = join
    return data


def model_post_screen_params_for_all(data: ModelScreenParamsForAll = None):
    """列表筛选参数"""
    order = []
    [order.extend(list(s.items())) for s in data.order]
    data.order = order
    where = [(w['key'], w['condition'], w['value']) for w in data.where if
             ('value' in w and (w['value'] or w['value'] is False or w['value'] == 0)) and (not "join" in w or "join" in w and not w['join'])]
    join = [(w['join'], [(w['key'], w['condition'], w['value'])], 'join') for w in data.where if
            ('value' in w and (w['value'] or w['value'] is False or w['value'] == 0)) and ("join" in w and w['join'])]
    data.where = where
    data.join = join
    return data


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
