""" smplchat.settings - Contains global settings like default ports """
from os import getenv

try:
    DEBUG
except NameError:
    DEBUG = getenv("DEBUG")

PORT = 62733
NODE_TIMEOUT = 300	# After 300s we can assume connection is lost
