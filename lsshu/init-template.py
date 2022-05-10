if __name__ == '__main__':
    from lsshu.oauth.model import Model, Engine
    from lsshu.demo.model import permission as permission_demo

    Model.metadata.create_all(Engine)  # 创建表结构

    APP_PERMISSIONS = [
        permission_demo
    ]

    from config import OAUTH_ADMIN_USERS
    from lsshu.internal.helpers import store_permissions, init_user_and_password

    store_permissions(APP_PERMISSIONS)  # 初始化权限
    init_user_and_password(OAUTH_ADMIN_USERS)  # 初始化授权用户
