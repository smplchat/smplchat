""" smplchat.settings - Contains global settings like default ports """
from os import getenv
from sys import stderr
from ipaddress import IPv4Address


# adjust these constants to your liking to change system behavior
settings = {

# network settings
"PORT": (int, 62733),		# adjust listener port

# gossip protocol parameters
"GOSSIP_FANOUT": (int, 2),	# how many random peers gossipped to
"RELAY_SEEN_LIMIT": (int, 2),	# seen limit for a chat/join/leave/keepalive relay


# timeout settings (seconds)
"NODE_TIMEOUT": (int, 300),	# After 300s we can assume connection is lost
"KEEPALIVE_INTERVAL": (int, 2),	# keepalive's interval
"CLEANUP_INTERVAL": (int, 60),	# how often list cleanup (msg, keepalive, client) occurs

# message history settings
"LATEST_LIMIT": (int, 50),	# latest msgs spread with relays, also affects JOIN_REPLY
"MAX_MESSAGES": (int, 2000),	# max number of messages in history, can be >2000 before cleanup


# optional overrides mainy for testing (leave as is to use default behaviour)
"DEBUG": (str, None),		# set to something to print out DEBUG information to stderr
"DROP_PERCENT": (int, 0),	# testing option to adjust how many percent of dispached packets to be dropped
"NICK": (str, None),		# Sets nick beforehand
"JOIN": (IPv4Address, None)	# Gives join command as first action when app is up and running

}



ENV_PREFIX="SMPLCHAT_"
def env_or_default(var):
    """ Tries to read enviroment varable, but if not valid or not there uses default"""
    if var not in globals():
        try:
            env_value = getenv(ENV_PREFIX+var)
            if not env_value:
                return settings[var][1]
            return settings[var][0](env_value)
        except ValueError:
            print(f"Ignoring invalid {ENV_PREFIX+var} environmental variable",
                file=stderr)
            return settings[var][1]
    return globals()[var]


GOSSIP_FANOUT = env_or_default("GOSSIP_FANOUT")
RELAY_SEEN_LIMIT = env_or_default("RELAY_SEEN_LIMIT")
NODE_TIMEOUT = env_or_default("NODE_TIMEOUT")
KEEPALIVE_INTERVAL = env_or_default("KEEPALIVE_INTERVAL")
CLEANUP_INTERVAL = env_or_default("CLEANUP_INTERVAL")
LATEST_LIMIT = env_or_default("LATEST_LIMIT")
MAX_MESSAGES = env_or_default("MAX_MESSAGES")
DEBUG = env_or_default("DEBUG")
PORT = env_or_default("PORT")
DROP_PERCENT = env_or_default("DROP_PERCENT")
NICK = env_or_default("NICK")
JOIN = env_or_default("JOIN")
