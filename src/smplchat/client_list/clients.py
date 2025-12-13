""" clients - ClientList class is defined here """
from ipaddress import IPv4Address
from time import time
from random import sample
from smplchat.settings import NODE_TIMEOUT

class ClientList:
    """ Adds, Removes, and Timeouts other nodes addresses """
    def __init__(self, own_ip: IPv4Address):
        self.__own: IPv4Address = own_ip
        self.__iplist: dict[IPv4Address, int] = {}

    def add(self, ip_addr:IPv4Address):
        """ Adds ip address to the list or updates timestamp """
        if ip_addr != self.__own:
            self.__iplist[ip_addr] = int(time())

    def add_list(self, ip_addresses: list[IPv4Address]):
        """ Adds list of ip addresses to the list """
        for x in ip_addresses:
            self.add(x)

    def cleanup(self):
        """ Cleans up ip addresses that we havent heard of in some time """
        cur_ts = int(time())
        for ip_addr, ts in list(self.__iplist.items()):
            if cur_ts - ts > NODE_TIMEOUT:
                del self.__iplist[ip_addr]

    def get(self, n, exclude: IPv4Address = None) -> list[IPv4Address]:
        """ Returns random n-list of ip addresses currently involved """
        peers = list(self.__iplist.keys())
        if exclude and exclude in peers:
            peers.remove(exclude)
        if len(peers) <= n:
            return peers
        return sample(peers, n)

    def get_all(self) -> list[IPv4Address]:
        """ Returns all peers """
        return list(self.__iplist.keys())

    # unused remove and clear, undo commenting if needed
    #def remove(self, ip_addr):
    #    """ Remove specific ip from the list """
    #    self.__iplist.pop(ip_addr, None)

    #def clear(self):
    #    """ Removes all ips from the list """
    #    self.__iplist.clear()
