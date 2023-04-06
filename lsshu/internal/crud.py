from typing import Union, List, Tuple

from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from lsshu.internal.db import Model


class BaseCRUD(object):
    params_pk = "id"
    params_model = Model  # 操作模型
    params_db = Session  # db实例
    params_query = None  # 查询实例
    params_relation: dict = {}  # 关联表 用于join等
    params_relationship: dict = {}  # 多对多时使用
    params_action_method: list = [
        "start", "pseudo_deletion", "query", "where", "join", "order",
        "page", "offset", "limit", "end"
        # "page", "offset", "limit", "clear_params", "end"
    ]
    params: dict = {
        "where": [],  # 查询条件
        "order": [],  # 排序
    }

    @classmethod
    def init(cls, model, db=None, pk="id"):
        """
        初始化
        :param model:
        :param db:
        :param pk:
        :return:
        """
        cls.params_model = model
        cls.params_db = db
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
        return cls

    @classmethod
    def db(cls, db):
        """
        设定 db
        :param db:
        :return:
        """
        cls.params_db = db
        cls.action_clear_params()
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
        query = cls.action_params(**kwargs).action().params_query
        return query.all()

    @classmethod
    def count(cls, **kwargs) -> int:
        """
        多数据
        :param kwargs:
        :return:
        """
        data = cls.action_params(**kwargs).action().params_query.count()
        return data

    @classmethod
    def first(cls, **kwargs):
        """
        单条数据
        :param kwargs:
        :return:
        """
        data = cls.action_params(**kwargs).action().params_query.first()
        return data

    @classmethod
    def paginate(cls, **kwargs):
        """
        分页 操作
        :param kwargs:
        :return:
        """
        import math
        items = cls.action_params(**kwargs).action().params_query.all()
        limit = cls.params.get('limit', 0)
        total = cls.action_params(**kwargs).action_clear_params(('limit', 'page', 'offset')).action().params_query.count()
        pages = math.ceil(total / limit) if type(total) is int and type(limit) is int and limit != 0 else 1
        return {
            "items": items,  # 当前页的数据列表
            "pages": pages,  # 总页数
            "total": total,  # 总条数
            "limit": limit,  # 页条数
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
        return db_item

    @classmethod
    def update(cls, **kwargs):
        """
        更新模型数据
        :param kwargs:
        :return:
        """
        item = cls._update_relationship(**kwargs)
        exclude_unset = kwargs.get('exclude_unset', False)
        cls.action_params(**kwargs).action().params_query.update(
            item.dict(exclude_unset=exclude_unset)), cls.params_db.commit(), cls.params_db.close()
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
                elif hasattr(item, relation) and relation in item.dict(exclude_unset=True):
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
        query = cls.action_params(**kwargs).action().params_query
        response = query.delete()
        cls.params_db.commit(), cls.params_db.close()
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
        if bool(where):
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
                cls.filter_where(where=w) if w else None
        cls.params.update({"where": []})
        return cls

    @classmethod
    def join(cls, join: Union[list, tuple, None] = None):
        """
        join=[('sale', [('status', True)], 'join')]
        :param join:
        :return:
        """
        if bool(join):
            _join = cls.params.get('join', [])
            if (type(join) == list or type(join) == tuple) and (type(join[0]) == list or type(join[0]) == tuple):
                _join.extend(join)
            elif (type(join) == list or type(join) == tuple) and type(join[0]) == str:
                _join.append(join)
            cls.params.update({"join": _join})
        return cls

    @classmethod
    def action_join(cls):
        """
        过滤模型数据条件
        :return:
        """
        join = cls.params.get('join', None)
        if join and (type(join) == tuple or type(join) == list):  # 设置过滤 like
            for j in join:
                if j:
                    join_model = cls.params_relation.get(j[0], None)
                    if join_model:
                        cls.params_query = getattr(cls.params_query, j[2] if len(j) == 3 and j[2] else 'join')(join_model)
                        for w in j[1]:
                            cls.filter_where(where=w, model=join_model) if join_model else None
        cls.params.update({"join": []})
        return cls

    @classmethod
    def filter_where(cls, where: Union[list, tuple, None] = None, model=None):
        """
        过滤数据条件
        :param where:
        :param model:
        :return:
        """
        query = cls.params_query
        params_model = cls.params_model if not model else model
        if bool(where) and (type(where) == tuple or type(where) == list):
            if len(where) == 2 and (type(where[0]) is list or type(where[0]) is tuple) and where[1] == "or":
                """([('content',"==", '东'),('content','==', '西')], 'or')"""
                _filters = [cls.filter_item(params_model, fil) for fil in where[0]]
                query = query.filter(or_(*_filters))
            else:
                query = query.filter(cls.filter_item(params_model, where))
        cls.params_query = query
        return cls

    @classmethod
    def filter_item(cls, model, where):
        if len(where) == 2:
            """('content', '西')"""
            if type(where[0]) is str:
                return getattr(model, where[0]) == where[1]
        elif len(where) == 3:
            if where[1] == "==" or where[1] == "=" or where[1] == "eq":
                """('content', '==', '西')"""
                return getattr(model, where[0]) == where[2]
            elif where[1] == "!=" or where[1] == "<>" or where[1] == "><" or where[1] == "neq" or where[1] == "ne":
                """('content', '!=', '西')"""
                return getattr(model, where[0]) != where[2]
            elif where[1] == ">" or where[1] == "gt":
                """('content', '>', '西')"""
                return getattr(model, where[0]) > where[2]
            elif where[1] == ">=" or where[1] == "ge":
                """('content', '>=', '西')"""
                return getattr(model, where[0]) >= where[2]
            elif where[1] == "<" or where[1] == "lt":
                """('content', '<', '西')"""
                return getattr(model, where[0]) < where[2]
            elif where[1] == "<=" or where[1] == "le":
                """('content', '<=', '西')"""
                return getattr(model, where[0]) <= where[2]
            elif where[1] in ["like", "ilike"]:
                if not where[2] is None:
                    """('content', 'like', '西')"""
                    return getattr(getattr(model, where[0]), where[1])("%" + where[2] + "%")
            elif where[1] in ["or"]:
                if type(where[0]) == tuple or type(where[0]) == list:
                    """(['name','content'], 'or', '西')"""
                    _filters = [(getattr(model, fil) == where[2]) for fil in where[0]]
                    return or_(*_filters)

                if type(where[0]) == str and (type(where[2]) == tuple or type(where[2]) == list):
                    """('name', 'or', ['西', '西'])"""
                    _filters = [(getattr(model, where[0]) == fil) for fil in where[2]]
                    return or_(*_filters)
            elif where[1] in ["or_like", "or_ilike"]:
                if type(where[0]) == tuple or type(where[0]) == list:
                    """(['name','content'], 'or_like', '西')"""
                    _filters = [(getattr(getattr(model, fil), where[1][3:])("%" + where[2] + "%")) for
                                fil in
                                where[0]]
                    return or_(*_filters)
                if type(where[0]) == str and (type(where[2]) == tuple or type(where[2]) == list):
                    """('name', 'or_like', ['西', '西'])"""
                    _filters = [(getattr(getattr(model, where[0]), where[1][3:])("%" + fil + "%")) for
                                fil in
                                where[2]]
                    return or_(*_filters)
            elif where[1] in ["between"] and type(where[2]) in [list, tuple] and len(where[2]) == 2:
                return getattr(getattr(model, where[0]), where[1])(where[2][0], where[2][1])
            elif where[1] in ["datebetween"] and type(where[2]) in [list, tuple] and len(where[2]) == 2:
                return getattr(getattr(model, where[0]), 'between')(where[2][0], where[2][1])
            elif where[1] in ["datetimebetween"] and type(where[2]) in [list, tuple] and len(where[2]) == 2:
                return getattr(getattr(model, where[0]), 'between')("%s 00:00:00" % where[2][0], "%s 23:59:59" % where[2][1])
            elif where[1] in ["in"] and type(where[2]) in [list, tuple]:
                return getattr(getattr(model, where[0]), "in_")(where[2])
            elif where[1] in ["notin"] and type(where[2]) in [list, tuple]:
                return getattr(getattr(model, where[0]), "notin_")(where[2])
            else:
                return getattr(getattr(model, where[0]), where[1])(where[2])
        return

    @classmethod
    def order(cls, order: Union[List[tuple], List[list], Tuple[tuple], Tuple[list], list, tuple]):
        """
        排序
        :param order:
        :return:
        """
        if bool(order):
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
            if orders and (type(orders) == tuple or type(orders) == list):  # 设置排序
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
    def screen_params(cls, params: BaseModel):
        cls.action_params(**params.dict())
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
            if "where" in kwargs:
                del kwargs['where']
            return cls.update(**kwargs, pk=getattr(instance, cls.params_pk), exclude_unset=True)
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
            return nodes

        def json_fields_fun(node):
            import copy
            _node = copy.deepcopy(node)
            return {"id": _node.id, "label": _node.name, "node": _node}

        return cls.params_model.get_tree(session=db, json=json, json_fields=json_fields_fun if json is True and not json_fields else json_fields,
                                         query=query if query else query_fun)
