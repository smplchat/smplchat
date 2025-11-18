""" smplchat.packet_mangler.packer - functions to form data from message classes """
from smplchat.settings import dprint
from .message import (
    Message,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    KeepaliveRelayMessage,
    JoinRequestMessage,
    JoinReplyMessage,
    OldRequestMessage,
    OldReplyMessage)


def packer(msg: Message):
    """ packer - packs message to binary data for sending """
    if isinstance(msg, ChatRelayMessage):
        pass
    elif isinstance(msg, JoinRelayMessage):
        pass
    elif isinstance(msg, LeaveRelayMessage):
        pass
    elif isinstance(msg, KeepaliveRelayMessage):
        pass
    elif isinstance(msg, JoinRequestMessage):
        pass
    elif isinstance(msg, JoinReplyMessage):
        pass
    elif isinstance(msg, OldRequestMessage):
        pass
    elif isinstance(msg, OldReplyMessage):
        pass
    else:
        dprint("ERROR: unknown message type in packer")
