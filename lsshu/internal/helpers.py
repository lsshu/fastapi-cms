def token_verify_password(plain_password: str, hashed_password: str):
    """
    验证 oauth token密码
    :param plain_password: 明文密码
    :param hashed_password: hash 密码
    :return: bool
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    return False if not hashed_password else pwd_context.verify(plain_password, hashed_password)


def token_get_password_hash(password: str):
    """
    给 oauth user 加密
    :param password: 加密密码
    :return: hash
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    return pwd_context.hash(password)


def token_access_token(data: dict, key: str, algorithm: str, expires_delta):
    """
    生成 token
    :param data: 加密数据
    :param key: 加密key
    :param algorithm: 加密 算法
    :param expires_delta: 有效期 类型 timedelta
    :return: token
    """
    from datetime import datetime, timedelta
    from jose import jwt
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=key, algorithm=algorithm)
    return encoded_jwt


def token_payload(security_scopes, token, key, algorithm):
    """
    获取 当前授权用户数据
    :param security_scopes: SecurityScopes
    :param token: OAuth2PasswordBearer
    :param key: 加密key
    :param algorithm: 加密 算法
    :return:
    """
    from jose import jwt, JWTError
    from fastapi import HTTPException, status
    from pydantic import ValidationError
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Could not validate credentials',
                                          headers={"WWW-Authenticate": authenticate_value})
    try:
        payload = jwt.decode(token=token, key=key, algorithms=[algorithm])
        sub: str = payload.get('sub')
        if sub is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
    except (JWTError, ValidationError):
        raise credentials_exception
    """排除不授权限管理"""
    # Todo
    """排除不授权限管理"""
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions",
                                headers={"WWW-Authenticate": authenticate_value})
    return payload


def store_permissions(permissions: list):
    """
    创建权限
    :param permissions:
    :return:
    """
    from lsshu.oauth.model import SYSTEM_PERMISSIONS
    # 检查其它权限
    checkPermissionOrStore(permissions)
    # 检查系统权限
    checkPermissionOrStore(SYSTEM_PERMISSIONS)


def checkPermissionOrStore(permissions: list, db=None, parent_pk: int = None):
    """
    检查或者创建权限
    :param permissions:
    :param db:
    :param parent_pk:
    :return:
    """
    from lsshu.oauth.permission.crud import CRUDOAuthPermission
    from lsshu.oauth.permission.schema import SchemasOAuthPermissionStoreUpdate
    ACTION_ITEMS = [
        {"name": "列表", "scope": "list"},
        {"name": "详情", "scope": "get"},
        {"name": "创建", "scope": "store"},
        {"name": "更新", "scope": "update"},
        {"name": "删除", "scope": "delete"},
        {"name": "导出", "scope": "download"},
    ]
    if not db:
        from lsshu.internal.db import SessionLocal
        db = SessionLocal()
    for permission in permissions:
        _scope = permission.get('scope')
        _name = permission.get('name')
        _action = permission.get('action', [])
        _children = permission.get('children', None)
        _is_menu = permission.get('is_menu', True)
        _is_action = permission.get('is_action', True)
        icon = permission.get('icon', None)
        parent = CRUDOAuthPermission.find_or_store_model(
            db=db, where=('scope', _scope), item=SchemasOAuthPermissionStoreUpdate(
                name=_name, scope=_scope, parent_id=parent_pk, is_menu=_is_menu, is_action=_is_action, icon=icon
            )
        )
        if _children:
            checkPermissionOrStore(_children, db=db, parent_pk=parent.id)
        else:
            for action in (ACTION_ITEMS + _action):
                scope = "%s.%s" % (_scope, action.get('scope'))
                name = "%s %s" % (_name, action.get('name'))
                is_menu = action.get('is_menu', False)
                is_action = action.get('is_action', True)
                CRUDOAuthPermission.find_or_store_model(
                    db=db, where=('scope', scope), item=SchemasOAuthPermissionStoreUpdate(
                        name=name, scope=scope, parent_id=parent.id, is_menu=is_menu, is_action=is_action
                    )
                )


def init_user_and_password(users: dict):
    """
    重置账号密码
    :param users: {username:password}
    :return:
    """
    from lsshu.oauth.user.crud import CRUDOAuthUser, SchemasOAuthUserStoreUpdate
    from lsshu.internal.db import SessionLocal
    db = SessionLocal()
    return [CRUDOAuthUser.update_or_store_model(db=db, where=('username', username), item=SchemasOAuthUserStoreUpdate(username=username, password=password))
            for username, password in users.items()]
