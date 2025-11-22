""" message.__init__ - Defines messages and implements generators """
from .message import (
    MessageType,
    Message,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    KeepaliveRelayMessage,
    JoinRequestMessage,
    JoinReplyMessage,
    OldRequestMessage,
    OldReplyMessage)
from .message_gen import new_message
