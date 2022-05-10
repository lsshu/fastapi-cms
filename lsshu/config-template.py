# API 接口返回数据
SCHEMAS_SUCCESS_CODE = 0
SCHEMAS_SUCCESS_STATUS = 'success'
SCHEMAS_SUCCESS_MESSAGE = '数据请求成功！'
SCHEMAS_ERROR_CODE = 1
SCHEMAS_ERROR_STATUS = 'error'
SCHEMAS_ERROR_MESSAGE = '数据请求失败！'

# 站点
HOST_URL = ""

# 上传目录
UPLOAD_NAME = "static"
UPLOAD_DIR = "static"
UPLOAD_URI = "/static"

# OAuth 授权相关
OAUTH_DEFAULT_TAGS = ['OAuth']
OAUTH_LOGIN_SCOPES = "login"

OAUTH_TOKEN_URL = "/api/token"
OAUTH_TOKEN_SCOPES = {
    OAUTH_LOGIN_SCOPES: OAUTH_LOGIN_SCOPES.capitalize()
}
OAUTH_SECRET_KEY = "4a876f7766d1a0e9d97231089be927e38d6dea09233ad212f056b7f1a75cd41d"
OAUTH_ALGORITHM = "HS256"
OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES = 300
OAUTH_OAUTH_ROUTER = {}

# 超级管理员 账号:密码
OAUTH_ADMIN_USERS = {
    "admin": "admin"
}

# 数据库相关
import os

DB_SQLALCHEMY_DATABASE_URL = "sqlite:///{}".format(os.path.join(os.path.dirname(__file__), 'db.sqlite3'))
# DB_SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@192.168.1.3:3306/ic"

# echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
# 由于SQLAlchemy是多线程，指定check_same_thread=False来让建立的对象任意线程都可使用。这个参数只在用SQLite数据库时设置
DB_ENGINE_KWARGS = {
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
DB_SESSION_MAKER_KWARGS = {
    "autoflush": False,
    "autocommit": False,
    "expire_on_commit": True
}
