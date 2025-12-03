""" client_list.keep_alive - simple class for accounting keepalive realy messages """
from dataclasses import dataclass
from time import time
from smplchat.settings import NODE_TIMEOUT

@dataclass
class KeepaliveEntry:
    """ entries for the list """
    def __init__(self):
        self.seen=1
        self.addtime=int(time())

class KeepaliveList:
    """ the list """
    def __init__(self):
        self.__entries={}

    def cleanup(self):
        """ cleans up too old entries """
        now = int(time())
        for uid, entry in self.__entries.items():
            if now - entry.addtime > NODE_TIMEOUT:
                del self.__entries[uid]

    def add(self, uid):
        """ add entry or update seen count"""
        if uid in self.__entries:
            self.__entries[uid].seen+=1
        else:
            self.__entries[uid]=KeepaliveEntry()

    def seen_count(self, uid):
        """ returns how many times we have seen this uid already """
        if not uid in self.__entries:
            return 0
        return self.__entries[uid].seen
