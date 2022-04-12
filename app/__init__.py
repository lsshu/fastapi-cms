from fastapi import APIRouter

from lsshu.oauth import router as router_oauth

router = APIRouter()
router.include_router(router_oauth)

from app.demo import router as router_demo
router.include_router(router_demo)

if __name__ == '__main__':
    from lsshu.db import Engine, Model

    from app.demo import APP_PERMISSION as PERMISSION_DEMO

    Model.metadata.create_all(Engine)  # 创建表结构

    APP_PERMISSIONS = [
        PERMISSION_DEMO
    ]

    from config import OAUTH_ADMIN_USERS
    from lsshu.oauth.helpers import store_permissions, init_user_and_password

    store_permissions(APP_PERMISSIONS)  # 初始化权限
    init_user_and_password(OAUTH_ADMIN_USERS)  # 初始化授权用户
