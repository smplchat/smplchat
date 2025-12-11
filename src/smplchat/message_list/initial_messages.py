""" message_list.initial_messages - Just helpers to get it all going """
from .list import MessageList

def initial_messages(ml: MessageList):
    """ Fill chat-log with some initial and helpful messages"""
    ml.sys_message("** Welcome to smplchat **")
    ml.sys_message("Short guide:")
    ml.sys_message("/join <ip-address> - join existing chat")
    ml.sys_message("/nick <nick>       - select nick for yourself")
    ml.sys_message("/quit              - quit the application")
    ml.sys_message("/peers             - list peers")
    ml.sys_message("<message>          - say something to others")
