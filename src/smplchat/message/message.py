""" smplchat.message - message dataclasses are defined here """
from dataclasses import dataclass
from enum import IntEnum

class MessageType(IntEnum):
    """ Different types of allowed message types and corresponding int """
    CHAT_RELAY = 0
    JOIN_RELAY = 1
    LEAVE_RELAY = 2
    KEEPALIVE_RELAY = 3
    JOIN_REQUEST = 128
    JOIN_REPLY = 129
    OLD_REQUEST = 130
    OLD_REPLY = 131

@dataclass
class Message:
    """ message - basis for every type of message """

@dataclass
class RelayMessage(Message):
    """ relay message - messages that are distributed as is in the system """

@dataclass
class ChatRelayMessage(RelayMessage):
    """ chat relay message - actual messages send by users """
    msg_type: int
    uniq_msg_id: int
    sender_ip: int
    old_message_ids: list[int]
    sender_nick: str
    msg_text: str

@dataclass
class JoinRelayMessage(RelayMessage):
    """ join relay message - the message formed by client that handles join request """
    msg_type: int
    uniq_msg_id: int
    sender_ip: int
    old_message_ids: list[int]
    sender_nick: str

@dataclass
class LeaveRelayMessage(RelayMessage):
    """ leave relay message - send by client leaving the chat """
    msg_type: int
    uniq_msg_id: int
    sender_ip: int
    old_message_ids: list[int]
    sender_nick: str

@dataclass
class KeepaliveRelayMessage(Message):
    """ keepalive relay message - time to time relay message to be distributed for
                                  other clients not to consider client disconnected.
    """
    msg_type: int
    uniq_msg_id: int
    sender_ip: int

@dataclass
class JoinRequestMessage(Message):
    """ join request message - the first message client sends to join the chat """
    msg_type: int
    uniq_msg_id: int
    sender_nick: str

@dataclass
class JoinReplyMessage(Message):
    """ join reply message - informs newly joined client about history and ip:s"""
    msg_type: int
    old_message_ids: list[int]
    ip_addresses: list[int]

@dataclass
class OldRequestMessage(Message):
    """ old request message - message to request message by id """
    msg_type: int
    uniq_msg_id: int

@dataclass
class OldReplyMessage(Message):
    """ old reply message - reply for old message request """
    msg_type: int
    old_msg_type: int
    uniq_msg_id: int
    sender_nick: str
    msg_text: str
