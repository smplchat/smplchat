""" listener.py - smplchat.listener """
import socket
import threading
from ipaddress import IPv4Address
from threading import Lock

from smplchat.settings import SMPLCHAT_PORT
from smplchat.utils import dprint

class Listener:
    """ Listener - a class for receiving UDP packets """
    def __init__(self, self_ip: IPv4Address = IPv4Address("0.0.0.0")):
        self.__msg_queue: list[tuple[bytes, IPv4Address]] = []
        self.__msg_lock: Lock = threading.Lock()

        self.__port = SMPLCHAT_PORT
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        address = (str(self_ip), self.__port)
        self._sock.bind(address)
        self._sock.settimeout(0.1)

        self.__stop = False
        self.__thread = threading.Thread(target=self.__listener_loop, name="listener")
        self.__thread.start()

    def __listener_loop(self):
        while not self.__stop:
            try:
                data, addr = self._sock.recvfrom(10000)
                self.__append_msg(data, IPv4Address(addr[0]))
            except socket.timeout:
                continue # no data for 0.1 s
            except OSError as e:
                if not self.__stop:
                    dprint(f"Listener socket error: {e}")
                break

    def __append_msg(self, data: bytes, ip_addr: IPv4Address):
        with self.__msg_lock:
            self.__msg_queue.append((data, ip_addr))

    def get_messages(self) -> list[tuple[bytes, IPv4Address]]:
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
