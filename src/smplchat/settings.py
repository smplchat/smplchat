""" smplchat.settings - Contains global settings like default ports """
from os import getenv

if "DEBUG" not in globals():
    DEBUG = getenv("DEBUG")

PORT = 62733
NODE_TIMEOUT = 300	# After 300s we can assume connection is lost
#KEEPALIVE_INTERVAL = 30 # keepalive's interval in seconds
