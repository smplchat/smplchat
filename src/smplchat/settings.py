""" smplchat.settings - Contains global settings like default ports """
from os import getenv
from sys import stderr

if "DEBUG" not in globals():
    DEBUG = getenv("DEBUG")

if "PORT" not in globals():
    try:
        PORT = int(getenv("SMPLCHAT_PORT") or 62733)
    except ValueError:
        PORT = 62733
        print("Ignoring invalid SMPLCHAT_PORT enviromental variable",
                file=stderr)

NODE_TIMEOUT = 300	# After 300s we can assume connection is lost
KEEPALIVE_INTERVAL = int(NODE_TIMEOUT/2) # keepalive's interval in seconds
