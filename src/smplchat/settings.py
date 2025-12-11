""" smplchat.settings - Contains global settings like default ports """
from os import getenv
from sys import stderr
from ipaddress import IPv4Address

# these "if" constants aren't generally to be modified unlike constants at bottom
# they may simply get their value from the env

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

if "SMPLCHAT_NICK" not in globals():
    SMPLCHAT_NICK = getenv("SMPLCHAT_NICK")

if "SMPLCHAT_JOIN" not in globals():
    try:
        SMPLCHAT_JOIN = IPv4Address(getenv("SMPLCHAT_JOIN"))
    except ValueError:
        SMPLCHAT_JOIN = None

# adjust these bottom constants to your liking to change system behavior

NODE_TIMEOUT = 300	# After 300s we can assume connection is lost
KEEPALIVE_INTERVAL = 2 # keepalive's interval in seconds
LATEST_LIMIT = 50 # latest msgs spread with relays, note: JOIN_REPLY is multiplier of this
