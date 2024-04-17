import json
import socket

from . import _get_config

config = _get_config()


def submit(fn, *args, **kwargs):
    """
    :param fn: It must be a callable object, or a string in the format package.module:name.
    :param args: callable object's args
    :param kwargs: callable object's kwargs
    :return: str or None. task id if str, submitting fail if None,
    """
    if callable(fn):
        fn = "%s:%s" % (fn.__module__, fn.__name__)

    data = {
        "fn": fn,
        "args": args,
        "kwargs": kwargs
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((config[0], config[1]))
        s.sendall(json.dumps(data).encode("utf8") + b"\n\n")
        data = s.recv(512)
        s.close()

    if data.startswith(b"ok"):
        return data.lstrip(b"ok").decode("utf8")
