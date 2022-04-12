from typing import Optional, Union, List, Tuple

from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from config import SCHEMAS_SUCCESS_CODE, SCHEMAS_SUCCESS_STATUS, SCHEMAS_SUCCESS_MESSAGE
from lsshu.db import Model


class BaseCRUD(object):
    params_pk = "id"
    params_delete_tag = "deleted_at"  # 伪删除 字段
    params_model = Model  # 操作模型
    params_db = Session  # db实例
    params_query = None  # 查询实例
    params_pseudo_deletion = False  # 伪删除
    params_choose_pseudo_deletion = True  # 是否添加伪删除前提 默认是
    params_relationship: dict = {}  # 多对多时使用
    params_action_method: list = [
        "start", "pseudo_deletion", "query", "where", "order",
        "page", "offset", "limit", "clear_params", "end"
    ]
    params: dict = {
        "where": [],  # 查询条件
        "order": [],  # 排序
    }

    @classmethod
    def init(cls, model, db=None, pseudo_deletion=False, pk="id"):
        """
        初始化
        :param model:
        :param pseudo_deletion:
        :param db:
        :param pk:
        :return:
        """
        cls.params_model = model
        cls.params_db = db
        cls.params_pseudo_deletion = pseudo_deletion
        cls.params_pk = pk
        return cls

    @classmethod
    def action_clear_params(cls, name: Union[str, list, tuple, None] = None):
        """
        清除参数条件
        :param name:
        :return:
        """
        if name and type(name) == str:
            if name in cls.params:
                del cls.params[name]
        elif name and (type(name) == list or type(name) == tuple):
            for n in name:
                if n in cls.params:
                    del cls.params[n]
        else:
            cls.params.clear()

        # 重置伪删除
        setattr(cls, '_params_choose_pseudo', cls.params_choose_pseudo_deletion)
        setattr(cls, '_params_pseudo', cls.params_pseudo_deletion)
        return cls

    @classmethod
    def action_pseudo_deletion(cls):
        """
        是否伪删除 操作
        :return:
        """
        choose = getattr(cls, '_params_choose_pseudo', cls.params_choose_pseudo_deletion)
        pseudo_deletion = getattr(cls, '_params_pseudo', cls.params_pseudo_deletion)
        if choose and pseudo_deletion:
            cls.where(cls.params_delete_tag, 'is_', None)
        return cls

    @classmethod
    def db(cls, db):
        """
        设定 db
        :param db:
        :return:
        """
        cls.params_db = db
        return cls

    @classmethod
    def pseudo_deletion(cls, pseudo: bool):
        """
        设定是否 伪删除
        :param pseudo:
        :return:
        """
        cls._params_pseudo = pseudo
        return cls

    @classmethod
    def choose_pseudo_deletion(cls, choose: bool):
        """
        设定是否 伪删除操作 临时
        :param choose:
        :return:
        """
        cls._params_choose_pseudo = choose
        return cls

    @classmethod
    def all(cls, **kwargs):
        """
        多数据
        :param kwargs:
        :return:
        """
        data = cls.action_params(**kwargs).action().params_query.all()
        cls.action_clear_params()
        return data

    @classmethod
    def removed(cls, **kwargs):
        """
        伪删除数据
        :param kwargs:
        :return:
        """
        data = cls.choose_pseudo_deletion(False).where(cls.params_delete_tag, 'is_not', None).action_params(
            **kwargs).action().params_query.all()
        cls.action_clear_params()
        return data

    @classmethod
    def recovery(cls, **kwargs):
        """
        恢复 伪删除数据
        :param kwargs:
        :return:
        """
        data = cls.choose_pseudo_deletion(False).where(cls.params_delete_tag, 'is_not', None).action_params(
            **kwargs).action().params_query.update({cls.params_delete_tag: None})
        cls.action_clear_params()
        return data

    @classmethod
    def first(cls, **kwargs):
        """
        单条数据
        :param kwargs:
        :return:
        """
        data = cls.action_params(**kwargs).action().params_query.first()
        cls.action_clear_params()
        return data

    @classmethod
    def paginate(cls, **kwargs):
        """
        分页 操作
        :param kwargs:
        :return:
        """
        import math
        cls.action_params(**kwargs)
        page = cls.params.get('page', 1)
        limit = cls.params.get('limit', 0)

        items = cls.action().params_query.all()
        total = cls.action_clear_params(('limit', 'page', 'offset')).action().params_query.count()
        pages = math.ceil(total / limit) if type(total) is int and type(limit) is int and limit != 0 else 1
        next_num = page + 1 if pages > page else None
        prev_num = page - 1 if page > 1 else None
        cls.action_clear_params()
        return {
            "has_next": bool(next_num),  # 如果下一页存在，返回True
            "has_prev": bool(prev_num),  # 如果上一页存在，返回True
            "items": items,  # 当前页的数据列表
            "next_num": next_num,  # 下一页的页码
            "prev_num": prev_num,  # 上一页的页码
            "page": page,  # 当前页码
            "pages": pages,  # 总页数
            "per_page": limit,  # 每页的条数
            "total": total,  # 总条数
        }

    @classmethod
    def store(cls, db: Session, item: BaseModel, **kwargs):
        """
        创建模型数据
        :param db:
        :param item:
        :param kwargs:
        :return:
        """
        cls.action_params(db=db, **kwargs)
        # 处理关联
        import copy
        _item = copy.deepcopy(item)
        if type(cls.params_relationship) is dict:
            for relation in cls.params_relationship:
                if hasattr(item, relation) and bool(getattr(item, relation)):
                    delattr(item, relation)
        # 创建实例
        db_item = cls.params_model(**kwargs, **item.dict(exclude_unset=True))
        # 添加关联
        if type(cls.params_relationship) is dict:
            for (relation, relation_class) in cls.params_relationship.items():
                if hasattr(_item, relation) and bool(getattr(_item, relation)):
                    _relation = BaseCRUD.all(model=relation_class, db=db, where=(
                        "id", 'in_', getattr(_item, relation)))
                    setattr(db_item, relation, _relation)

        cls.params_db.add(db_item)
        cls.params_db.commit()
        cls.params_db.refresh(db_item)
        cls.action_clear_params()
        return db_item

    @classmethod
    def update(cls, **kwargs):
        """
        更新模型数据
        :param kwargs:
        :return:
        """
        item = cls._update_relationship(**kwargs)
        cls.action_params(**kwargs).action().params_query.update(
            item.dict(exclude_unset=True)), cls.params_db.commit(), cls.params_db.close()
        cls.action_clear_params()
        return cls.first(**kwargs)

    @classmethod
    def _update_relationship(cls, db: Session, item: BaseModel, **kwargs):
        """
        更新处理关联 多对多
        :param db:
        :param item:
        :return:
        """
        if type(cls.params_relationship) is dict:
            for (relation, relation_class) in cls.params_relationship.items():
                _obj = cls.first(db=db, **kwargs)
                if hasattr(item, relation) and bool(getattr(item, relation)):
                    _relation = BaseCRUD.all(db=db, model=relation_class, where=(
                        "id", 'in_', getattr(item, relation)))
                    setattr(_obj, relation, _relation)
                    db.add(_obj), db.commit(), db.close()
                elif hasattr(item, relation):
                    [getattr(_obj, relation).remove(rela) for rela in getattr(_obj, relation)]
                delattr(item, relation)
        return item

    @classmethod
    def delete(cls, **kwargs):
        """
        删除多模型数据
        :param kwargs:
        :return:
        """
        from datetime import datetime

        query = cls.action_params(**kwargs).action().params_query
        response = query.update(
            {cls.params_delete_tag: datetime.now()}) if cls.params_pseudo_deletion else query.delete()
        cls.params_db.commit(), cls.params_db.close()
        cls.action_clear_params()
        return response

    @classmethod
    def action_query(cls):
        """
        获取查询实例
        :return:
        """
        cls.params_query = cls.params_db.query(cls.params_model)
        return cls

    @classmethod
    def pk(cls, pk: int):
        """
        设定查询 主键
        :param pk:
        :return:
        """
        cls.where(cls.params_pk, pk)
        return cls

    @classmethod
    def pks(cls, pks: Union[List[int], Tuple[int]]):
        """
        设定查询 多主键
        :param pks:
        :return:
        """
        pks = list(pks) if type(pks) == tuple else pks
        cls.where(cls.params_pk, 'in_', pks)
        return cls

    @classmethod
    def model(cls, model):
        """
        设定 操作模型
        :param model:
        :return:
        """
        cls.params_model = model
        return cls

    @classmethod
    def where(cls, where: Union[List[tuple], List[list], Tuple[tuple], Tuple[list], list, tuple, str], *args):
        """
        添加查询 条件
        :param where:
        :return:
        """
        _where = cls.params.get('where', [])
        if (type(where) == list or type(where) == tuple) and (type(where[0]) == list or type(where[0]) == tuple):
            _where.extend(where)
        elif (type(where) == list or type(where) == tuple) and type(where[0]) == str:
            _where.append(where)
        elif type(where) == str:
            _where.append((where, *args))
        cls.params.update({"where": _where})
        return cls

    @classmethod
    def action_where(cls):
        """
        过滤模型数据条件
        :return:
        """
        where = cls.params.get('where', None)
        if where and (type(where) == tuple or type(where) == list):  # 设置过滤 like
            for w in where:
                cls.filter_where(where=w)
        return cls

    @classmethod
    def filter_where(cls, where: Union[list, tuple, None] = None):
        """
        过滤数据条件
        :param where:
        :return:
        """
        query = cls.params_query
        if bool(where) and (type(where) == tuple or type(where) == list):
            if len(where) == 2:
                """('content', '西')"""
                query = query.filter(getattr(cls.params_model, where[0]) == where[1])
            elif len(where) == 3:
                if where[1] == "==":
                    """('content', '==', '西')"""
                    query = query.filter(getattr(cls.params_model, where[0]) == where[2])
                elif where[1] == "!=" or where[1] == "<>" or where[1] == "><":
                    """('content', '!=', '西')"""
                    query = query.filter(getattr(cls.params_model, where[0]) != where[2])
                elif where[1] == ">":
                    """('content', '>', '西')"""
                    query = query.filter(getattr(cls.params_model, where[0]) > where[2])
                elif where[1] == ">=":
                    """('content', '>=', '西')"""
                    query = query.filter(getattr(cls.params_model, where[0]) >= where[2])
                elif where[1] == "<":
                    """('content', '<', '西')"""
                    query = query.filter(getattr(cls.params_model, where[0]) < where[2])
                elif where[1] == "<=":
                    """('content', '<=', '西')"""
                    query = query.filter(getattr(cls.params_model, where[0]) <= where[2])
                elif where[1] in ["like", "ilike"]:
                    if not where[2] is None:
                        """('content', 'like', '西')"""
                        query = query.filter(
                            getattr(getattr(cls.params_model, where[0]), where[1])("%" + where[2] + "%")
                        )
                elif where[1] in ["or"]:
                    if type(where[0]) == tuple or type(where[0]) == list:
                        """(['name','content'], 'or', '西')"""
                        _filters = [(getattr(cls.params_model, fil) == where[2]) for fil in where[0]]
                        query = query.filter(or_(*_filters))

                    if type(where[0]) == str and (type(where[2]) == tuple or type(where[2]) == list):
                        """('name', 'or', ['西', '西'])"""
                        _filters = [(getattr(cls.params_model, where[0]) == fil) for fil in where[2]]
                        query = query.filter(or_(*_filters))
                elif where[1] in ["or_like", "or_ilike"]:
                    if type(where[0]) == tuple or type(where[0]) == list:
                        """(['name','content'], 'or_like', '西')"""
                        _filters = [(getattr(getattr(cls.params_model, fil), where[1][3:])("%" + where[2] + "%")) for
                                    fil in
                                    where[0]]
                        query = query.filter(or_(*_filters))
                    if type(where[0]) == str and (type(where[2]) == tuple or type(where[2]) == list):
                        """('name', 'or_like', ['西', '西'])"""
                        _filters = [(getattr(getattr(cls.params_model, where[0]), where[1][3:])("%" + fil + "%")) for
                                    fil in
                                    where[2]]
                        query = query.filter(or_(*_filters))
                else:
                    query = query.filter(getattr(getattr(cls.params_model, where[0]), where[1])(where[2]))
        cls.params_query = query
        return cls

    @classmethod
    def order(cls, order: Union[List[tuple], List[list], Tuple[tuple], Tuple[list], list, tuple]):
        """
        排序
        :param order:
        :return:
        """
        _order = cls.params.get('order', [])
        if type(order[0]) == list or type(order[0]) == tuple:
            _order.extend(order)
        elif type(order[0]) == str:
            _order.append(order)
        cls.params.update({"order": _order})
        return cls

    @classmethod
    def action_order(cls):
        """
        处理排序到查询
        :return:
        """
        query = cls.params_query
        orders = cls.params.get('order', [])
        if bool(orders):
            if orders and (type(orders) == tuple or type(orders) == list):  # 设置过滤 like
                for attr_item in orders:
                    query = query.order_by(getattr(getattr(cls.params_model, attr_item[0]), attr_item[1])())
        cls.params_query = query
        return cls

    @classmethod
    def page(cls, page: int):
        """
        设置page页
        :param page:
        :return:
        """
        cls.params.update({"page": page})
        return cls

    @classmethod
    def action_page(cls):
        """
        处理分页到查询
        :return:
        """
        query = cls.params_query
        page = cls.params.get('page', None)
        limit = cls.params.get('limit', None)
        if bool(page) and type(page) is int and bool(limit):
            offset = (page - 1) * limit
            query = query.offset(offset)

        cls.params_query = query
        return cls

    @classmethod
    def offset(cls, offset: int):
        """
        :param offset:
        :return:
        """
        cls.params.update({"offset": offset})
        return cls

    @classmethod
    def action_offset(cls):
        """
        :return:
        """
        query = cls.params_query
        offset = cls.params.get('offset', None)
        limit = cls.params.get('limit', None)
        if bool(offset) and bool(limit):
            query = query.offset(offset)
        cls.params_query = query
        return cls

    @classmethod
    def limit(cls, limit: int):
        """
        :param limit:
        :return:
        """
        cls.params.update({"limit": limit})
        return cls

    @classmethod
    def action_limit(cls):
        """
        :return:
        """
        query = cls.params_query
        limit = cls.params.get('limit', None)
        offset = cls.params.get('offset', None)
        page = cls.params.get('page', None)
        if bool(limit) and (bool(offset) or bool(page)):
            query = query.limit(limit)
        cls.params_query = query
        return cls

    @classmethod
    def action(cls):
        """处理查询参数 params 到 query"""
        [(getattr(cls, "action_%s" % action)() if hasattr(cls, "action_%s" % action) else None) for action in
         cls.params_action_method]
        return cls

    @classmethod
    def action_params(cls, **kwargs):
        """
        处理kwargs 参数到 params
        :param kwargs:
        :return:
        """
        [(getattr(cls, params)(params_value) if hasattr(cls, params) else None) for params, params_value in
         kwargs.items()]
        return cls

    @classmethod
    def update_or_store_model(cls, **kwargs):
        """
        更新或者创建
        :param kwargs:
        :return:
        """
        instance = cls.first(**kwargs)
        if instance:
            return cls.update(**kwargs, pk=getattr(instance, cls.params_pk))
        else:
            del kwargs['where']
            return cls.store(**kwargs)

    @classmethod
    def find_or_store_model(cls, **kwargs):
        """
        查找或者创建
        """
        instance = cls.first(**kwargs)
        if not instance:
            del kwargs['where']
            return cls.store(**kwargs)
        return instance


class CRUDTree(BaseCRUD):
    @classmethod
    def move_inside(cls, db: Session, inside_id: int, **kwargs):
        """
        移动到 inside_id 下
        :param db:
        :param inside_id:
        :param kwargs:
        :return:
        """
        node = cls.first(db=db, **kwargs)
        return node.move_inside(inside_id)

    @classmethod
    def move_after(cls, db: Session, after_id: int, **kwargs):
        """
        移动到 after_id 后
        :param db:
        :param after_id:
        :param kwargs:
        :return:
        """
        node = cls.first(db=db, **kwargs)
        return node.move_after(after_id)

    @classmethod
    def get_tree(cls, db: Session, json=False, json_fields=None, query=None):
        """
        获取树
        :param db:
        :param json:
        :param json_fields:
        :param query:
        :return:
        """

        def query_fun(nodes):
            return nodes.filter(getattr(cls.params_model, cls.params_delete_tag).is_(None))

        if json:
            def json_fields(node):
                import copy
                _node = copy.deepcopy(node)
                delattr(_node, cls.params_delete_tag)
                return {"id": _node.id, "label": _node.name, "node": _node}
        return cls.params_model.get_tree(session=db, json=json, json_fields=json_fields, query=query if query else query_fun)


class Schemas(BaseModel):
    """状态返回"""
    code: Optional[int] = SCHEMAS_SUCCESS_CODE
    status: Optional[str] = SCHEMAS_SUCCESS_STATUS
    message: Optional[str] = SCHEMAS_SUCCESS_MESSAGE
    data: Optional[Union[dict, list, str, None]] = None


class SchemasPaginate(BaseModel):
    has_next: bool  # 如果下一页存在，返回True
    has_prev: bool  # 如果上一页存在，返回True
    items: list  # 当前页的数据列表
    next_num: Union[int, None]  # 下一页的页码
    prev_num: Union[int, None]  # 上一页的页码
    page: Union[int, None]  # 当前页码
    pages: int  # 总页数
    per_page: Union[int, None]  # 每页的条数
    total: int  # 总条数


def hashids_encode(ids: int, **kwargs):
    """
    hashids 加密
    :param ids:
    :param kwargs:
    :return:
    """
    from hashids import Hashids
    hashids = Hashids(**kwargs)
    return hashids.encode(ids)


def hashids_decode(string: str, **kwargs):
    """
    hashids 解密
    :param string:
    :param kwargs:
    :return:
    """
    from hashids import Hashids
    hashids = Hashids(**kwargs)
    return hashids.decode(string)


def get_mac_address():
    """
    获取 本机 mac 地址
    :return:
    """
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def get_host_name():
    """
    获取主机名
    :return:
    """
    import socket
    return socket.getfqdn(socket.gethostname())


def get_host_ip():
    """
    获取IP地址
    :return:
    """
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_client_ip(request):
    """
    获取请求的ip
    :param request:
    :return:
    """
    headers = request.headers
    addr = headers.get('http_x_forwarded_for', None)
    if not addr:
        addr = headers.get('http_client_ip', None)
    if not addr:
        addr = headers.get('remote_addr', None)
    if not addr:
        addr = headers.get('remote-host', None)
    if not addr:
        addr = headers.get('x-real-ip', None)
    if not addr:
        addr = headers.get('x-forwarded-for', None)
    if not addr:
        addr = headers.get('x-forwarded-for', None)
    return addr or None


def md5_string(string):
    """
    md5 字符串
    :param string:
    :return:
    """
    import hashlib
    md5hash = hashlib.md5(string.encode('utf8'))
    return md5hash.hexdigest()


def md5_file(file):
    """
    md5 文件
    :param file:
    :return:
    """
    import hashlib
    m = hashlib.md5()
    with open(file, 'rb') as obj:
        while True:
            data = obj.read(4096)
            if not data:
                break
            m.update(data)

    return m.hexdigest()


def str_bytes(string: str, **kwargs):
    """
    字符串转字节
    :param string:
    :param kwargs:
    :return:
    """
    return bytes(string, **kwargs)


def bytes_str(b: bytes, **kwargs):
    """
    字节转字符串
    :param b:
    :param kwargs:
    :return:
    """
    return str(b, **kwargs)


def plural(word: str):
    """
    字符串转复制
    :param word:
    :return:
    """
    if word.endswith('y'):
        return word[:-1] + "ies"
    elif word[-1] in 'sx' or word[-2:] in ["sh", "ch"]:
        return word + "es"
    elif word.endswith('an'):
        return word[:-2] + "en"
    else:
        return word + "s"
