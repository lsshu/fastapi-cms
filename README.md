# Lsshu 
_admin@lsshu.cn_

## 安装
```shell
pip install lsshu-cms
```
#### 其它依赖
```shell
pip install uvicorn fastapi sqlalchemy sqlalchemy_mptt python-multipart hashids passlib python-jose bcrypt websockets
```
## 使用
_1、在项目根目录新建文件 **`main.py`**_ 
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import router

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
app.include_router(router)
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

_2、在项目根目录新建python包 **`app`** 在包app下打开文件 **`__init__.py`**_ 
```python
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

```

_3、在包app下新建python包 **`demo`** 在包demp下打开文件 **`__init__.py`**_ 
```python
from fastapi import APIRouter
from app.demo.project import router as router_project, permission as permission_project

router = APIRouter()
router.include_router(router_project)

name = __name__.capitalize()
APP_PERMISSION = {
    "name": "demo", "scope": name, "children": [
        permission_project
    ]
}

```

_4、在包demo下新建文件 **`project.py`**_ 
```python
"""
XX操作
"""
from datetime import datetime
from typing import Optional, List

from fastapi import Security, Depends, APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import Session

from lsshu import BaseCRUD, Schemas, SchemasPaginate, plural
from lsshu.db import dbs, Model
from lsshu.oauth import SchemasOAuthScopes, auth_user

name = plural(__name__.capitalize())
scopes = [name, ]
tags = [name, ]
permission = {"name": "project", "scope": name, "action": [{"name": "pro", "scope": "pro"}]}


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


table_name = name.replace('.', '_')


class Models(Model):
    """ 模型 """
    __tablename__ = table_name
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(15), nullable=False, unique=True, comment="名称")
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.now, comment="创建日期")
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新日期")
    deleted_at = Column(TIMESTAMP, nullable=True, comment="删除日期")


class CRUD(BaseCRUD):
    """表操作"""
    params_model = Models
    params_pseudo_deletion = True  # 伪删除


router = APIRouter()


@router.get('/{}'.format(name), name="get {}".format(name), tags=tags)
async def models(db: Session = Depends(dbs), page: Optional[int] = 1, limit: Optional[int] = 25,
                 name: Optional[str] = None, auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes)):
    """
    :param db:
    :param page:
    :param limit:
    :param name:
    :param auth:
    :return:
    """
    db_list = CRUD.paginate(db=db, page=page, limit=limit, where=("name", "like", name))
    return Schemas(data=SchemasPaginateItem(**db_list))


@router.get('/{}/{{pk}}'.format(name), name="get {}".format(name), tags=tags)
async def get_model(pk: int, db: Session = Depends(dbs),
                    auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes)):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    db_model = CRUD.first(db=db, pk=pk)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="{} not found".format(name.capitalize()))
    return Schemas(data=SchemasResponse(**db_model.to_dict()))


@router.post('/{}'.format(name), name="get {}".format(name), tags=tags)
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


@router.put("/{}/{{pk}}".format(name), name="update {}".format(name), tags=tags)
async def update_model(pk: int, item: SchemasStoreUpdate, db: Session = Depends(dbs),
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="{} not found".format(name.capitalize()))
    bool_model = CRUD.update(db=db, pk=pk, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@router.delete("/{}/{{pk}}".format(name), name="delete {}".format(name), tags=tags)
async def delete_model(pk: int, db: Session = Depends(dbs),
                       auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pk:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(name), name="deletes {}".format(name), tags=tags)
async def delete_models(pks: List[int], db: Session = Depends(dbs),
                        auth: SchemasOAuthScopes = Security(auth_user, scopes=scopes + ["%s.delete" % name])):
    """
    :param pks:
    :param db:
    :param auth:
    :return:
    """
    bool_model = CRUD.delete(db=db, pks=pks)
    return Schemas(data=bool_model)

```

_5、在根目录下新建文件 **`config.py`**_ 
```python
# API 接口返回数据
SCHEMAS_SUCCESS_CODE = 0
SCHEMAS_SUCCESS_STATUS = 'success'
SCHEMAS_SUCCESS_MESSAGE = '数据请求成功！'
SCHEMAS_ERROR_CODE = 1
SCHEMAS_ERROR_STATUS = 'error'
SCHEMAS_ERROR_MESSAGE = '数据请求失败！'

# OAuth 授权相关
OAUTH_DEFAULT_TAGS = ['OAuth']
OAUTH_LOGIN_SCOPES = "login"

OAUTH_TOKEN_URL = "/token"
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

```

_6、在根目录下新建文件 **`.gitignore`**_ 
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
RUN mkdir -p /app && pip install uvicorn fastapi sqlalchemy sqlalchemy_mptt python-multipart hashids passlib python-jose bcrypt websockets
EXPOSE 80
WORKDIR /app
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