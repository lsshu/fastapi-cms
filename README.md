# Lsshu 
_admin@lsshu.cn_

## 安装
```shell
pip install lsshu-cms
```

## 使用
_1、在项目根目录新建文件 **`main.py`**_ 
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lsshu.oauth.main import router as router_oauth

app = FastAPI(
    title='Base API Docs',
    description='Base API接口文档',
    version='1.0.0'
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_oauth, prefix="/api")
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

_2、在项目根目录新建python包 **`app`** 在包app下打开文件 **`__init__.py`**_ 
```python
if __name__ == '__main__':
    from lsshu.oauth.model import Model, Engine

    Model.metadata.create_all(Engine)  # 创建表结构

    APP_PERMISSIONS = []

    from config import OAUTH_ADMIN_USERS
    from lsshu.internal.helpers import store_permissions, init_user_and_password

    store_permissions(APP_PERMISSIONS)  # 初始化权限
    init_user_and_password(OAUTH_ADMIN_USERS)  # 初始化授权用户
```

_3、在包app下新建python包 **`demo`** 在包demp下新建文件 **`model.py`**_ 
```python
from sqlalchemy import Column, String

from lsshu.internal.db import Model
from lsshu.internal.method import plural

name = plural(__name__.capitalize())
table_name = name.replace('.', '_')
permission = {"name": "Demo", "scope": name, "action": [{"name": "de", "scope": "de"}]}


class Models(Model):
    """ 模型 """
    __tablename__ = table_name
    name = Column(String(15), nullable=False, unique=True, comment="名称")
```

_4、在包demo下新建文件 **`crud.py`**_ 
```python
from lsshu.demo.model import Models
from lsshu.internal.crud import BaseCRUD


class CRUD(BaseCRUD):
    """表操作"""
    params_model = Models
```

_5、在包demo下新建文件 **`schema.py`**_ 
```python
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from lsshu.internal.schema import SchemasPaginate


class SchemasResponse(BaseModel):
    """模型 返回"""
    id: int
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasStoreUpdate(BaseModel):
    """模型 提交"""
    name: Optional[str] = None


class SchemasPaginateItem(SchemasPaginate):
    items: List[SchemasResponse]


class SchemasParams(BaseModel):
    pass
```
_6、在包demo下新建文件 **`main.py`**_ 
```python
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session

from lsshu.internal.db import dbs
from lsshu.internal.depends import model_screen_params, model_post_screen_params, auth_user
from lsshu.internal.schema import ModelScreenParams, Schemas
from lsshu.oauth.user.schema import SchemasOAuthScopes

from .crud import CRUD
from .model import name as name
from .schema import SchemasResponse, SchemasParams, SchemasPaginateItem, SchemasStoreUpdate

router = APIRouter(tags=["Demo"])
scopes = [name, ]


@router.get('/{}'.format(name), name="get {}".format(name))
async def get_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.list" % name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUD.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.post('/{}.post'.format(name), name="post {}".format(name))
async def post_models(db: Session = Depends(dbs), params: ModelScreenParams = Depends(model_post_screen_params),
                     auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.list" % name])):
    """
    :param db:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CRUD.paginate(db=db, screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.get('/{}.params'.format(name), name="get {}".format(name))
async def params_models(db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.list" % name])):
    """
    :param db:
    :param auth:
    :return:
    """

    data = {}
    return Schemas(data=SchemasParams(**data))


@router.get('/{}/{{pk}}'.format(name), name="get {}".format(name))
async def get_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.get" % name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{} not found".format(name.capitalize()))
    return Schemas(data=SchemasResponse(**db_model))


@router.post('/{}'.format(name), name="get {}".format(name))
async def store_model(item: SchemasStoreUpdate, db: Session = Depends(dbs),
                      auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.store" % name])):
    """
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, where=("name", item.name))
    if db_model is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="{} already registered".format(name.capitalize()))
    bool_model = CRUD.store(db=db, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(name), name="update {}".format(name))
async def update_put_model(pk: int, item: SchemasStoreUpdate, db: Session = Depends(dbs),
                           auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.update" % name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{} not found".format(name.capitalize()))
    bool_model = CRUD.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}".format(name), name="update {}".format(name))
async def update_patch_model(pk: int, item: SchemasStoreUpdate, db: Session = Depends(dbs),
                             auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.update" % name])):
    """
    :param pk:
    :param item:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{} not found".format(name.capitalize()))
    bool_model = CRUD.update(db=db, pk=pk, item=item, exclude_unset=True)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.delete("/{}/{{pk}}".format(name), name="delete {}".format(name))
async def delete_model(pk: int, db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(name), name="deletes {}".format(name))
async def delete_role_models(pks: List[int], db: Session = Depends(dbs), auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pks=pks)
    return Schemas(data=bool_model)
```
_7、在根目录下新建文件 **`config.py`**_ 
```python
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
```

_8、在根目录下新建文件 **`.gitignore`**_ 
```gitignore
.idea
Desktop.ini
db.sqlite3
.DS_Store
*__pycache__*
```


### docker 部署
_1、在根目录下新建文件 **`Dockerfile`**_ 
```Dockerfile
FROM python:3.8
WORKDIR /app
EXPOSE 80
RUN mkdir -p /app && pip install lsshu-cms
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
```
_2、创建镜像并运行_ 
```shell
docker build -t project_name . && docker run -d --name project_name -v /projects/project_path:/app -p 49000:80 project_name
```
_@project_name 项目名称; /projects/project_path 项目所在的目录; 49000 宿主机端口; 80 容器端口;_

_3、删除容器和镜像_ 
```shell
docker stop project_name && docker rm project_name && docker rmi project_name
```

### nginx 部署
```nginx
http {
    upstream project_server { 
        server 0.0.0.0:49000 weight=1;
    }
    server{
        listen 80;
        server_name project.com;
        index index.html index.htm;
        root /projects/project_path/dist;
        
        try_files $uri $uri/ /index.html;
        
        location /static/ {
          alias /projects/project_path/static/; #静态资源路径
        }
        
        location  ~/api|/docs|/openapi.json
        {
          proxy_pass  http://project_server;
          # 配置websocket
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection "upgrade";
          # 其它代理
          proxy_set_header Http_Referer $http_referer;
          proxy_set_header Host $host:$server_port; 
          proxy_set_header X-real-ip $remote_addr;
        }
        location ~ ^/(\.user.ini|\.htaccess|\.git|\.svn|\.project|LICENSE|README.md|app|main\.py|config\.py)
        {
            return 404;
        }
    }
}
```
_@root /projects/project_path/dist 其中`dist` 可为前端打包的目录；其它根据自身增减_