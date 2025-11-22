""" clients - ClientList class is defined here """
from time import time
from random import choice
from smplchat.settings import NODE_TIMEOUT

class ClientList:
    """ Adds, Removes, and Timeouts other nodes addresses """
    def __init__(self, own_ip):
        self.__own = own_ip
        self.__iplist = {}

    def add(self, ip_addr):
        """ Adds ip address to the list or updates timestamp """
        if ip_addr != self.__own:
            self.__iplist[ip_addr] = int(time())

    def remove(self, ip_addr):
        """ Just removes ip from the list. For example on leave """
        if ip_addr in self.__iplist:
            del self.__iplist[ip_addr]

    def update(self):
        """ Cleans up ip addresses that we havent heard of in some time """
        cur_ts = int(time())
        for ip_addr, ts in self.__iplist:
            if cur_ts - ts > NODE_TIMEOUT:
                del self.__iplist[ip_addr]

    def get(self, n = 2):
        """ Returns random n-list of ip addresses currently involved """
        if len(self.__iplist) <= n:
            return self.__iplist.keys()
        selected={}
        while len(selected) < n:
            selected.update(choice(self.__iplist))
        return selected.keys()
