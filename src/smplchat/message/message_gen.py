""" smplchat.message_gen - functions to generate messages """
from smplchat.utils import generate_uid, dprint
from smplchat.settings import LATEST_LIMIT
from .message import (
    MessageType,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    KeepaliveRelayMessage,
    JoinRequestMessage,
    JoinReplyMessage,
    OldRequestMessage,
    OldReplyMessage)

def new_message(msg_type: MessageType, **kwargs):
    """ Generates new message. TODO: move this in better place
        msg_type	- As defined in MessageType Enum

        Optional parameters:
        nick		- Sets nick of sender
        text		- Actual text of message (used in CHAT_RELAY, OLD_REPLY)
        ip		- Neened in RELAY messages to distribute ipadresses
                          and update keepalive status.
        msg_list	- Needed in RELAY messages and JOIN_REPLY for
                          for gathiring information of past messages
        client_list	- Needed only in JOIN_REPLY
        uid		- uid of message. Needen in OLD_REQUEST and OLD_REPLY
    """
    uid = generate_uid()
    try:
        match msg_type:
            case MessageType.CHAT_RELAY:
                return ChatRelayMessage(
                    uniq_msg_id = uid,
                    sender_ip = kwargs["ip"],
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=LATEST_LIMIT),
                    sender_nick = kwargs["nick"],
                    msg_text = kwargs["text"])

            case MessageType.JOIN_RELAY:
                return JoinRelayMessage(
                    uniq_msg_id = uid,
                    sender_ip = kwargs["ip"],
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=LATEST_LIMIT),
                    sender_nick = kwargs["nick"])

            case MessageType.LEAVE_RELAY:
                return LeaveRelayMessage(
                    uniq_msg_id = uid,
                    sender_ip = kwargs["ip"],
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=LATEST_LIMIT),
                    sender_nick = kwargs["nick"])

            case MessageType.KEEPALIVE_RELAY:
                return KeepaliveRelayMessage(
                    uniq_msg_id=uid,
                    sender_ip=kwargs["ip"],
                )

            case MessageType.JOIN_REQUEST:
                return JoinRequestMessage(
                    uniq_msg_id = uid,
                    sender_nick = kwargs["nick"])

            case MessageType.JOIN_REPLY:
                return JoinReplyMessage(
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=LATEST_LIMIT * 2),
                    ip_addresses = kwargs["client_list"].get() )

            case MessageType.OLD_REQUEST:
                return OldRequestMessage(
                    uniq_msg_id = kwargs["uid"] )

            case MessageType.OLD_REPLY:
                return OldReplyMessage(
                    uniq_msg_id = kwargs["uid"],
                    sender_nick = kwargs["nick"],
                    msg_text = kwargs["text"] )

    except KeyError as e:
        dprint(f"Cannot create message. Problem with new_message parameters.\n{e}")
        raise KeyError from e

    dprint(f"Could not create message with message type: {msg_type}")
    return None
