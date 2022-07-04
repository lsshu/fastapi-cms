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


def md5_bytes(string: bytes):
    """
    md5 字符串
    :param string:
    :return:
    """
    import hashlib
    md5hash = hashlib.md5(string)
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


def write_file(path, content, mode="wb", **kwargs):
    """
    写入文件
    :param path:
    :param content:
    :param mode:
    :param kwargs:
    :return:
    """
    import os
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    if not os.path.isdir(path):
        with open(path, mode, **kwargs) as f:
            f.write(content)
        return True
    else:
        return False
