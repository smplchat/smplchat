""" smplchat.message_gen - functions to generate messages """
from smplchat.utils import generate_uid, dprint
from .message import (
    MessageType,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
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
        old_type		- Type on old message. Needed in OLD_REPLY
    """
    uid = generate_uid()
    try:
        match msg_type:
            case MessageType.CHAT_RELAY:
                return ChatRelayMessage(
                    msg_type = MessageType.CHAT_RELAY,
                    uniq_msg_id = uid,
                    sender_ip = kwargs["ip"],
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=50),
                    sender_nick = kwargs["nick"],
                    msg_text = kwargs["text"])

            case MessageType.JOIN_RELAY:
                return JoinRelayMessage(
                    msg_type = MessageType.JOIN_RELAY,
                    uniq_msg_id = uid,
                    sender_ip = kwargs["ip"],
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=50),
                    sender_nick = kwargs["nick"])

            case MessageType.LEAVE_RELAY:
                return LeaveRelayMessage(
                    msg_type = MessageType.LEAVE_RELAY,
                    uniq_msg_id = uid,
                    sender_ip = kwargs["ip"],
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=50),
                    sender_nick = kwargs["nick"])

            case MessageType.JOIN_REQUEST:
                return JoinRequestMessage(
                    msg_type = MessageType.JOIN_REQUEST,
                    uniq_msg_id = uid,
                    sender_nick = kwargs["nick"])

            case MessageType.JOIN_REPLY:
                return JoinReplyMessage(
                    msg_type = MessageType.JOIN_REPLY,
                    old_message_ids = kwargs["msg_list"].latest_ids(limit=100),
                    ip_addresses = kwargs["client_list"].get() )

            case MessageType.OLD_REQUEST:
                return OldRequestMessage(
                    msg_type = MessageType.OLD_REQUEST,
                    uniq_msg_id = kwargs["uid"] )

            case MessageType.OLD_REPLY:
                return OldReplyMessage(
                    msg_type = MessageType.OLD_REPLY,
                    old_msg_type = kwargs["old_type"],
                    uniq_msg_id = kwargs["uid"],
                    sender_nick = kwargs["nick"],
                    msg_text = kwargs["text"] )

    except KeyError as e:
        dprint(f"Cannot create message. Problem with new_message parameters.\n{e}")
        raise KeyError from e

    dprint(f"Could not create message with message type: {msg_type}")
    return None
