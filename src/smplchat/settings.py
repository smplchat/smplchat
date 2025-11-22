""" smplchat.settings - Contains global settings like default ports """
from os import getenv
from sys import stderr

DEBUG = getenv("DEBUG")
PORT = 62733
NODE_TIMEOUT = 300	# After 300s we can assume connection is lost

def dprint(*args, **kwargs):
    """ dprint - just as print, but prints to stderr only if DEBUG is defined """
    if DEBUG:
        print(*args, **kwargs, file=stderr)
