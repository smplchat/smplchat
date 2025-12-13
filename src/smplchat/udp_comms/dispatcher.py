""" Dispatch - Just simple UDP data sending class """
from random import random
from ipaddress import IPv4Address
from socket import socket, AF_INET, SOCK_DGRAM
from smplchat.settings import SMPLCHAT_PORT, SMPLCHAT_DROP_PERCENT
from smplchat.message import Message
from .packer import packer

class Dispatcher:
    """ Class for sending UPD packets """
    def __init__(self):
        # possible permanent socket for very large scale use or due to firewall issues
        #self._sock = socket(AF_INET, SOCK_DGRAM)
        pass

    def send(self, msg: Message, ips: list[IPv4Address]):
        """ Method for sending a UPD packet """

        #FOR TESTING: Drop packets intentionally to simulate unreliable network
        if SMPLCHAT_DROP_PERCENT and random()*100 < SMPLCHAT_DROP_PERCENT:
            return

        with socket(AF_INET, SOCK_DGRAM) as sock:	# new UDP socket
            for ip in ips:
                sock.sendto( packer(msg), (str(ip), SMPLCHAT_PORT) )

    # Uncomment this and comment out above send to use permanent socket:
    #def send(self, msg: Message, ips: list[IPv4Address]):
    #    """ Method for sending a UPD packet (permanent socket version) """
    #    for ip in ips:
    #        self._sock.sendto(packer(msg), (str(ip), SMPLCHAT_PORT))
    #
    #def close(self):
    #    """ Socket cleanup, insert this at the main.py cleanup """
    #    self._sock.close()
