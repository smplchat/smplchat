""" smplchat.settings - Contains global settings like default ports """
from os import getenv
from sys import stderr
from ipaddress import IPv4Address

# adjust these constants to your liking to change system behavior

GOSSIP_FANOUT = 2 # how many random peers gossipped to
RELAY_SEEN_LIMIT = 2 # seen limit for a chat/join/leave/keepalive relay
NODE_TIMEOUT = 300	# After 300s we can assume connection is lost
KEEPALIVE_INTERVAL = 2 # keepalive's interval in seconds
CLEANUP_INTERVAL = 60 # how often list cleanup (msg, keepalive, client) occurs in seconds
LATEST_LIMIT = 50 # latest msgs spread with relays, note: JOIN_REPLY is multiplier of this
MAX_MESSAGES = 2000 # max number of messages in history, trimmed every CLEANUP_INTERVAL timer

# the following "if" constants aren't generally to be modified unlike above
# they may simply get their value from the env

if "DEBUG" not in globals():
    DEBUG = getenv("DEBUG")

if "SMPLCHAT_PORT" not in globals():
    try:
        SMPLCHAT_PORT = int(getenv("SMPLCHAT_PORT") or 62733)
    except ValueError:
        SMPLCHAT_PORT = 62733
        print("Ignoring invalid SMPLCHAT_PORT environmental variable",
                file=stderr)

if "SMPLCHAT_DROP_PERCENT" not in globals():
    try:
        SMPLCHAT_DROP_PERCENT = int(getenv("SMPLCHAT_DROP_PERCENT") or 0)
    except ValueError:
        SMPLCHAT_DROP_PERCENT = 0
        print("Ignoring invalid SMPLCHAT_DROP_PERCENT environmental variable",
                file=stderr)

if "SMPLCHAT_NICK" not in globals():
    SMPLCHAT_NICK = getenv("SMPLCHAT_NICK")

if "SMPLCHAT_JOIN" not in globals():
    try:
        SMPLCHAT_JOIN = IPv4Address(getenv("SMPLCHAT_JOIN"))
    except ValueError:
        SMPLCHAT_JOIN = None
