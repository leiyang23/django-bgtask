# coding=utf8
import json
import selectors
import socket
from logging import getLogger
from queue import Queue

from django.core.management.base import BaseCommand

from bgtask import core, _get_config

config = _get_config()
SERVER = (config[0], config[1])
WORK_THREADS = config[2]

_queue_size = 100

log = getLogger("django.bgtask")
sel = selectors.DefaultSelector()
executor = core.Executor(Queue(_queue_size), workers=WORK_THREADS)


def read_all(conn) -> bytes:
    data = b""
    while True:
        buf = conn.recv(2048)
        data += buf
        if len(buf) < 2048:
            break

    return data.rstrip(b"\n\n")


def accept(sock, mask):
    conn, addr = sock.accept()
    conn.setblocking(False)

    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask):
    data = read_all(conn)
    d = json.loads(data.decode("utf8"))
    try:
        task_id = executor.submit(d["fn"], *d["args"], **d["kwargs"])
        conn.send(b"ok" + task_id.encode("utf8"))
    except Exception as e:
        log.error(f"server error: {e}", exc_info=True)
        conn.send(b"error")

    sel.unregister(conn)
    conn.close()


class Command(BaseCommand):
    help = "django bgtask server"

    def handle(self, *args, **options):
        sock = socket.socket()
        sock.bind(SERVER)
        sock.listen(100)
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ, accept)
        log.info("""\n
        .########...######...########....###.....######..##....##
        .##.....##.##....##.....##......##.##...##....##.##...##.
        .##.....##.##...........##.....##...##..##.......##..##..
        .########..##...####....##....##.....##..######..#####...
        .##.....##.##....##.....##....#########.......##.##..##..
        .##.....##.##....##.....##....##.....##.##....##.##...##.
        .########...######......##....##.....##..######..##....##
        """)

        while True:
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
