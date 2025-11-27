""" clients - ClientList class is defined here """
from time import time
from random import sample
from smplchat.settings import NODE_TIMEOUT

class ClientList:
    """ Adds, Removes, and Timeouts other nodes addresses """
    def __init__(self, own_ip):
        self.__own = own_ip
        self.__iplist = {}

    def add(self, ip_addr):
        """ Adds ip address to the list or updates timestamp """
        if ip_addr != self.__own:
            self.__iplist[int(ip_addr)] = int(time())

    def add_list(self, ip_addresses: list[int]):
        """ Adds list of ip addresses to the list """
        for x in ip_addresses:
            self.add(x)

    def remove(self, ip_addr):
        """ Just removes ip from the list. For example on leave """
        self.__iplist.pop(ip_addr, None)

    def clear(self):
        """ Removes all ips from the list. """
        self.__iplist.clear()

    def update(self):
        """ Cleans up ip addresses that we havent heard of in some time """
        cur_ts = int(time())
        for ip_addr, ts in list(self.__iplist.items()):
            if cur_ts - ts > NODE_TIMEOUT:
                del self.__iplist[ip_addr]

    def get(self, n = 2):
        """ Returns random n-list of ip addresses currently involved """
        peers = list(self.__iplist.keys())
        if len(peers) <= n:
            return peers
        return sample(peers, n)
