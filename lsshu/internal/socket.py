import base64
import json

from pydantic import BaseModel
from typing import Optional, Union
from fastapi import WebSocket, WebSocketDisconnect

from lsshu.internal.redis import Redis, PickleSetObject


class WsState:
    """定义返回"""
    not_event = -1
    not_event_status = "error"
    success_code = 0
    success_status = "success"


class WsResponse(BaseModel):
    """状态返回"""
    code: Optional[int] = WsState.success_code
    status: Optional[str] = WsState.success_status
    event: Optional[str] = None
    data: Optional[Union[dict, list, str, None]] = None


class PickleSocket(PickleSetObject):
    socket = None


class WsEvents(object):
    self_socket: WebSocket = None
    redis: Redis = None

    def __init__(self, socket: WebSocket = None, redis: Redis = None):
        self.self_socket = socket
        self.redis = redis if redis else Redis()

    async def init(self):
        """
        分配事件给处理方法
        :param data:
        :return:
        """
        await self.self_socket.accept()
        try:
            while True:
                data = await self.self_socket.receive_text()
                data = self.decode(data)
                event = data.get('event', 'None')
                if hasattr(self, event):
                    data = data.get('data', None)
                    handle_data = await getattr(self, event)(data)
                    handle_data['event'] = handle_data.get("event", event)
                    await self.res_message(**handle_data)
                else:
                    await self.res_message(**data, code=WsState.not_event, status=WsState.not_event_status)
        except WebSocketDisconnect:
            pass

    def encode(self, data: dict) -> str:
        """
        字典转字符串 转base64
        :param data:
        :return:
        """
        return "lsshuey%s" % base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

    def decode(self, data: str) -> dict:
        """
        base64转json json转字典
        :param data:
        :return:
        """
        return json.loads(base64.b64decode(data[7:]).decode('utf-8'))

    def response(self, data=None, **kwargs) -> dict:
        """
        返回数据
        :param data:
        :param kwargs:
        :return:
        """
        return WsResponse(**kwargs, data=data).dict()

    async def auth(self, data) -> dict:
        """连接"""
        ps = PickleSocket(data)
        await self.redis.pickle_set("all-socket", ps)
        return {"data": "ok"}

    async def res_message(self, socket: WebSocket = None, **kwargs):
        """连接"""
        response_data = self.response(**kwargs)
        response = self.encode(response_data)
        await (self.self_socket if not socket else socket).send_text(response)

    async def message(self, data):
        """连接"""
        # await self.manager.broadcast(data)
        return {"data": ""}
