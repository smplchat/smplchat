""" smplchat.settings - Contains global settings like default ports """
from os import getenv
from sys import stderr

if "DEBUG" not in globals():
    DEBUG = getenv("DEBUG")

if "SMPLCHAT_PORT" not in globals():
    try:
        SMPLCHAT_PORT = int(getenv("SMPLCHAT_PORT") or 62733)
    except ValueError:
        SMPLCHAT_PORT = 62733
        print("Ignoring invalid SMPLCHAT_PORT enviromental variable",
                file=stderr)

if "SMPLCHAT_DROP_PERCENT" not in globals():
    try:
        SMPLCHAT_DROP_PERCENT = int(getenv("SMPLCHAT_DROP_PERCENT") or 0)
    except ValueError:
        SMPLCHAT_DROP_PERCENT = 0
        print("Ignoring invalid SMPLCHAT_DROP_PERCENT enviromental variable",
                file=stderr)

NODE_TIMEOUT = 300	# After 300s we can assume connection is lost
KEEPALIVE_INTERVAL = 2 #int(NODE_TIMEOUT/2) # keepalive's interval in seconds
LATEST_LIMIT = 50 # latest msgs spread with relays, note: JOIN_REPLY is multiplier of this
