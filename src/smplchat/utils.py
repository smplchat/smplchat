""" smplchat.utils - collection of small helper function """
from random import getrandbits
from time import time
from sys import stderr
from .settings import DEBUG

def generate_uid():
    """ Generates 64bit uid where half/half is time/random """
    return (int(time()) << 32) + getrandbits(32)

def get_time_from_uid(uid):
    """ Gets most significant bytes of uid which present time """
    return uid >> 32

def dprint(*args, **kwargs):
    """ dprint - just as print, but prints to stderr only if DEBUG is defined """
    if DEBUG:
        print(*args, **kwargs, file=stderr)
