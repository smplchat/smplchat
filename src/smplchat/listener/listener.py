import socket
import threading
from threading import Lock

from smplchat import settings

class Listener:

    def __init__(self):
        self.__msg_queue: list[bytes] = []
        self.__msg_lock: Lock = threading.Lock()

        self.__stop = False
        self.__thread = threading.Thread(target=self.__listener_loop, name="listener")
        self.__thread.start()


    def __listener_loop(self):
        s = socket.socket(type=socket.SOCK_DGRAM)
        address = ("", settings.PORT)
        s.bind(address)
        s.setblocking(False)

        while not self.__stop:
            try:
                recv = s.recv(10000)
                self.__append_msg(recv)
            except BlockingIOError as _:
                pass


    def __append_msg(self, data: bytes):
        with self.__msg_lock:
            self.__msg_queue.append(data)


    def get_messages(self) -> list[bytes]:
        ret = []
        with self.__msg_lock:
            ret = self.__msg_queue
            self.__msg_queue = []
        return ret


    def stop(self):
        self.__stop = True
        self.__thread.join()
