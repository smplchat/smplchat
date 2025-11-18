""" smplchat.settings - Contains global settings like default ports """
from os import getenv
from sys import stderr

DEBUG = getenv("DEBUG")

def dprint(*args, **kwargs):
    """ dprint - just as print, but prints to stderr only if DEBUG is defined """
    if DEBUG:
        print(*args, **kwargs, file=stderr)
