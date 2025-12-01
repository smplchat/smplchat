""" Dispatch - Just simple UDP data sending class """
from ipaddress import IPv4Address
from socket import socket, AF_INET, SOCK_DGRAM
from smplchat.settings import PORT
from smplchat.packet_mangler import packer
from smplchat.message import Message
from smplchat.utils import int_to_ip

class Dispatcher:
    """ Class for sending UPD packets """
    def __init__(self):
        pass

    def send(self, msg: Message, ips: list[IPv4Address]):
        """ Method for sending a UPD packet """
        with socket(AF_INET, SOCK_DGRAM) as sock:	# new UDP socket
            for ip in ips:
                sock.sendto( packer(msg), (str(ip), PORT) )
