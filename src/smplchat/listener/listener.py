""" listener.py - smplchat.listener """
import socket
import threading
import struct
from threading import Lock

from smplchat import settings

class Listener:
    """ Listener - a class for receiving UDP packets """
    def __init__(self):
        self.__msg_queue: list[tuple[bytes, tuple[str, int]]] = []
        self.__msg_lock: Lock = threading.Lock()

        self.__port = settings.PORT
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        address = ("", self.__port)
        self._sock.bind(address)
        self._sock.setblocking(False)

        self.__stop = False
        self.__thread = threading.Thread(target=self.__listener_loop, name="listener")
        self.__thread.start()

    @property
    def sock(self):
        """Let dispatcher use the same socket for peer discovery."""
        return self._sock

    def __listener_loop(self):
        while not self.__stop:
            try:
                data, addr = self._sock.recvfrom(10000)
                self.__append_msg(
                    data,
                    int(struct.unpack("=L", socket.inet_aton(addr[0]))[0]) )
            except BlockingIOError as _:
                pass

    def __append_msg(self, data: bytes, ip_addr: int):
        with self.__msg_lock:
            self.__msg_queue.append((data, ip_addr))

    def get_messages(self) -> list[(bytes, int)]:
        """ Method for retrieving messages from msg_queue """
        ret = []
        with self.__msg_lock:
            ret = self.__msg_queue
            self.__msg_queue = []
        return ret

    def stop(self):
        """ Method for stopping the thread and closing the socket """
        self.__stop = True
        self.__thread.join()
        try:
            self._sock.close()
        except OSError:
            pass
