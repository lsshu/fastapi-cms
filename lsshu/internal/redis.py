import aioredis
import pickle
from typing import Optional, Union, List, Tuple
from fastapi import FastAPI

try:
    from config import REDIS_CONFIG
except:
    REDIS_CONFIG = {
        "url": "redis://127.0.0.1:6379",
        "db": 10,
        "encoding": "utf-8",
        # "decode_responses": True
    }


class PickleSetObject(object):
    name = None

    def __init__(self, name: str):
        self.name = name


class Redis(object):
    key_prefix = None
    pool = None
    redis = None

    def __init__(self):
        self.pool = aioredis.ConnectionPool.from_url(**REDIS_CONFIG)
        self.redis = aioredis.Redis(connection_pool=self.pool)
        # """
        # https://blog.csdn.net/RoninYang/article/details/121128050
        # https://www.jianshu.com/p/e7f86bc09674?utm_campaign=maleskine
        # """
        # self.redis = app.state.redis = aioredis.from_url(**REDIS_CONFIG)
        #
        # @app.on_event("shutdown")
        # async def shutdown_event():
        #     app.state.redis.close() or app.state.redis.wait_closed()

    def __key(self, key, _type):
        """
        前缀键
        :param key:
        :param _type:
        :return:
        """
        return "%s-%s-%s" % (self.key_prefix, _type, key)

    def __value(self, value: Union[bytes, Tuple[bytes], List[bytes]], decode=True):
        """
        统一返回
        :param value:
        :param decode:
        :return:
        """
        return value if not decode else (
            value.decode() if type(value) is bytes else ([val.decode() for val in value] if type(value) is list else tuple([val.decode() for val in value])))

    async def string(self, key: str, value=None, default=None, decode=True):
        """
        设置字符串 或者 获取字符串
        :param key:
        :param value:
        :param default:
        :param decode:
        :return:
        """
        return await self.redis.set(self.__key(key, "string"), value) if value else (self.__value(await self.redis.get(self.__key(key, "string")), decode=decode) or default)

    async def hash(self, key: str, value: dict = None, field: Optional[Union[str, list]] = None, default=None, decode=True):
        """
        设置字符串 或者 获取 hash
        :param key:
        :param value:
        :param field:
        :param default:
        :param decode:
        :return:
        """
        if value:
            return await self.redis.hmset(self.__key(key, "hash"), value)
        else:
            data = self.__value(await self.redis.hmget(self.__key(key, "hash"), field), decode=decode)
            return (data if type(field) == list else data.pop()) or default

    async def list(self, key: str, value=None, default: list = [], start: int = 0, end: int = 10, decode=True):
        """
        设置或者获取 列表
        :param key:
        :param value:
        :param default:
        :param start:
        :param end:
        :param decode:
        :return:
        """
        return await self.redis.lpush(self.__key(key, "list"), value) if value else (
                self.__value((await self.redis.lrange(self.__key(key, "list"), start, end)), decode=decode) or default)

    async def list_remove(self, key: str, count, value):
        """
        移除列表的值
        :param key:
        :param count:
        :param value:
        :return:
        """
        return await self.redis.lrem(self.__key(key, "list"), count=count, value=value)

    async def set(self, key: str, value=None, default: tuple = tuple(), decode=True):
        """
        设置或者获取 列表
        :param key:
        :param value:
        :param default:
        :param decode:
        :return:
        """
        return await self.redis.sadd(self.__key(key, "set"), value) if value else (self.__value((await self.redis.smembers(self.__key(key, "set"))), decode=decode) or default)

    async def set_remove(self, key: str, value):
        """
        移除SET的值
        :param key:
        :param value:
        :return:
        """
        return await self.redis.smove(self.__key(key, "set"), value=value)

    async def sets(self, key: str, *value):
        """
        设置列表
        :param key:
        :param value:
        :return:
        """
        return await self.redis.sadd(self.__key(key, "set"), *value)

    async def pickle(self, key: str, value: object = None, default=None):
        """
        设置字符串 或者 获取字符串
        :param key:
        :param value:
        :param default:
        :return:
        """
        return await self.redis.set(self.__key(key, "pickle"), pickle.dumps(value)) if value else (pickle.loads(await self.redis.get(self.__key(key, "pickle"))) or default)

    async def pickle_set(self, key: str, value: PickleSetObject = None):
        """
        设置 pickle set
        :param key:
        :param value:
        :return:
        """
        if value:
            await self.set(self.__key(key, "pickle_set"), value.name)
            return await self.pickle(self.__key(value.name, "pickle_set"), value=value)
        else:
            keys = await self.set(self.__key(key, "pickle_set"))
            return tuple([await self.pickle(self.__key(se, "pickle_set")) for se in keys])

    async def delete(self, key: str, _type: str = "string"):
        """
        删除键值
        :param key:
        :param _type:
        :return:
        """
        return await self.redis.delete(self.__key(key, _type))

    async def disconnect(self):
        """
        断开链接
        :return:
        """
        await self.pool.disconnect()


async def _redis():
    redis = Redis()
    try:
        yield redis
    finally:
        await redis.disconnect()
