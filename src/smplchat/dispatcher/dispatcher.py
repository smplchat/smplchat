""" Dispatch - Just simple UDP data sending class """
from socket import socket, AF_INET, SOCK_DGRAM, inet_ntoa
from smplchat.settings import PORT
from smplchat.packet_mangler import packer
from smplchat.message import Message
from smplchat.utils import int_to_ip

class Dispatcher:
    """ Class for sending UPD packets """
    def __init__(self):
        pass

    def send(self, msg: Message, ips: list[int]):
        """ Method for sending a UPD packet """
        with socket(AF_INET, SOCK_DGRAM) as sock:	# new UDP socket
            for ip in ips:
                sock.sendto(
                        packer(msg),
                        (inet_ntoa(int_to_ip(ip)), PORT) )
