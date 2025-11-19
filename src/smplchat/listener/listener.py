import socket
import threading
from threading import Lock

from smplchat import settings

__msg_queue: list[bytes] = []
__msg_lock: Lock = threading.Lock()
__stop: bool = False
__thread: threading.Thread | None = None


def __listener_loop():
    s = socket.socket(type=socket.SOCK_DGRAM)
    address = ("", settings.PORT)
    s.bind(address)
    s.setblocking(False)

    while not __stop:
        try:
            recv = s.recv(10000)
            __append_msg(recv)
        except BlockingIOError as e:
            pass


def __append_msg(data: bytes):
    with __msg_lock:
        __msg_queue.append(data)


def get_messages() -> list[bytes]:
    ret = []
    with __msg_lock:
        global __msg_queue
        ret = __msg_queue
        __msg_queue = []
    return ret


def start():
    global __stop
    global __thread
    __stop = False
    __thread = threading.Thread(target=__listener_loop, name="listener")
    __thread.start()


def stop():
    global __thread
    global __stop
    __stop = True
    __thread.join()
