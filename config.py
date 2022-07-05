import os

ROOT_PATH = os.path.dirname(__file__)
# API 接口返回数据
SCHEMAS_SUCCESS_CODE: int = 0
SCHEMAS_SUCCESS_STATUS: str = 'success'
SCHEMAS_SUCCESS_MESSAGE: str = '数据请求成功！'
SCHEMAS_ERROR_CODE: int = 1
SCHEMAS_ERROR_STATUS: str = 'error'
SCHEMAS_ERROR_MESSAGE: str = '数据请求失败！'

# 站点
HOST_URL: str = ""

# 上传目录
UPLOAD_NAME: str = "static"
UPLOAD_DIR: str = "static"
UPLOAD_URI: str = "/static"

# OAuth 授权相关
OAUTH_DEFAULT_TAGS: list = ['OAuth']
OAUTH_LOGIN_SCOPES: str = "login"

OAUTH_TOKEN_URI: str = "/token"
OAUTH_TOKEN_URL: str = "/api%s" % OAUTH_TOKEN_URI
OAUTH_SCOPES_URI: str = "/scopes"
OAUTH_ME_URI: str = "/me"
OAUTH_TOKEN_SCOPES: dict = {
    OAUTH_LOGIN_SCOPES: OAUTH_LOGIN_SCOPES.capitalize()
}
OAUTH_SECRET_KEY: str = "4a876f7766d1a0e9d97231089be927e38d6dea09233ad212f056b7f1a75cd41d"
OAUTH_ALGORITHM: str = "HS256"
OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
OAUTH_OAUTH_ROUTER: dict = {}

# 超级管理员 账号:密码
OAUTH_ADMIN_USERS: dict = {
    "admin": "admin"
}

# 数据库相关
DB_SQLALCHEMY_DATABASE_URL: str = "sqlite:///{}".format(os.path.join(ROOT_PATH, 'db.sqlite3'))
# DB_SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@192.168.1.3:3306/ic" # ic 数据库

# echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
# 由于SQLAlchemy是多线程，指定check_same_thread=False来让建立的对象任意线程都可使用。这个参数只在用SQLite数据库时设置
DB_ENGINE_KWARGS: dict = {
    # "echo": True,
    # "encoding": 'utf-8',
    # "pool_pre_ping": True,
    # "pool_size": 100,
    # "pool_recycle": 3600,
    # "max_overflow": 100,
    "connect_args": {
        'check_same_thread': False,
        # "charset": "utf8mb4"
    }
}
# 在SQLAlchemy中，CRUD都是通过会话(session)进行的，所以我们必须要先创建会话，每一个SessionLocal实例就是一个数据库session
# flush()是指发送数据库语句到数据库，但数据库不一定执行写入磁盘；commit()是指提交事务，将变更保存到数据库文件
DB_SESSION_MAKER_KWARGS: dict = {
    "autoflush": False,
    "autocommit": False,
    "expire_on_commit": True
}
