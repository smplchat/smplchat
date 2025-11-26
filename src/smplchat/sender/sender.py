""" sender - Just simple UDP data sending class """
from ipaddress import IPv4Address
from socket import socket, AF_INET, SOCK_DGRAM, inet_ntoa
from smplchat.settings import PORT
from smplchat.packet_mangler import packer
from smplchat.message import Message


class Sender:
    def __init__(self):
        pass

    def send(self, msg: Message, ips: list[IPv4Address]):
        with socket(AF_INET, SOCK_DGRAM) as sock:  # new UDP socket
            for ip in ips:
                sock.sendto(packer(msg), (str(ip), PORT))
