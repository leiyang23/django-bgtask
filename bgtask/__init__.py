# coding=utf-8
import os
from django.conf import settings


def _get_config():
    if hasattr(settings, "BGTASK_SERVER_IP"):
        ip = settings.BGTASK_SERVER_IP
    else:
        ip = os.environ.get("BGTASK_SERVER_IP", "127.0.0.1")

    if hasattr(settings, "BGTASK_SERVER_PORT"):
        port = settings.BGTASK_SERVER_PORT
    else:
        port = os.environ.get("BGTASK_SERVER_PORT", 23323)

    if hasattr(settings, "BGTASK_WORK_THREADS"):
        work_threads = settings.BGTASK_SERVER_PORT
    else:
        work_threads = os.environ.get("BGTASK_WORK_THREADS", 10)

    return ip, port, work_threads
