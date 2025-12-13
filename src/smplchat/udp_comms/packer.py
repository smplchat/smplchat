""" smplchat.packet_mangler.packer - functions to form data from message classes """
from ipaddress import IPv4Address
from struct import pack, unpack, unpack_from
from smplchat.utils import dprint
from smplchat.message import (
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


def packer(m: Message):
    """ packer - packs message to binary data for sending """

    if isinstance(m, ChatRelayMessage):
        sender_nick = m.sender_nick.encode()
        msg_text = m.msg_text.encode()
        return pack(
            "!BQ4sLLL"
                f"{len(m.old_message_ids)}Q"
                f"{len(sender_nick)}s"
                f"{len(msg_text)}s",
            MessageType.CHAT_RELAY,			# B - 1 byte
            m.uniq_msg_id,				# Q - 8 bytes
            m.sender_ip.packed,				# 4s- 4 bytes
            len(m.old_message_ids),			# L - 4 bytes
            len(sender_nick),				# L - 4 bytes
            len(msg_text),				# L - 4 bytes

            *m.old_message_ids,				# ?Q - ? x 8 bytes
            sender_nick,				# ?s - ? chars (bytes)
            msg_text)					# ?s - ? * chars

    if isinstance(m, (JoinRelayMessage, LeaveRelayMessage)):
        sender_nick = m.sender_nick.encode()
        return pack(
            "!BQ4sLL"
                f"{len(m.old_message_ids)}Q"
                f"{len(sender_nick)}s",
            (MessageType.JOIN_RELAY if isinstance(m, JoinRelayMessage)
                    else MessageType.LEAVE_RELAY),	# B - 1 byte
            m.uniq_msg_id,				# Q - 8 bytes
            m.sender_ip.packed,				# 4s - 4 bytes
            len(m.old_message_ids),			# L - 4 bytes
            len(sender_nick),				# L - 4 bytes

            *m.old_message_ids,				# ?Q - ?x 8 bytes
            sender_nick)				# ?s - ? chars (bytes)

    if isinstance(m, KeepaliveRelayMessage):
        return pack(
            "!BQ4s",
            MessageType.KEEPALIVE_RELAY,		# B - 1 byte
            m.uniq_msg_id,				# Q - 8 bytes
            m.sender_ip.packed)				# L - 4 bytes

    if isinstance(m, JoinRequestMessage):
        sender_nick = m.sender_nick.encode()
        return pack(
            "!BQL"
                f"{len(sender_nick)}s",
            MessageType.JOIN_REQUEST,			# B - 1 byte
            m.uniq_msg_id,				# Q - 8 bytes
            len(sender_nick),				# L - 4 bytes

            sender_nick)				# ?s - ? chars (bytes)

    if isinstance(m, JoinReplyMessage):
        ips = bytearray()
        for ip in m.ip_addresses:
            ips += ip.packed
        return pack(
            "!BLL"
                f"{len(m.old_message_ids)}Q"
                f"{len(m.ip_addresses*4)}s",
            MessageType.JOIN_REPLY,			# B - 1 byte
            len(m.old_message_ids),			# L - 4 bytes
            len(m.ip_addresses),			# L - 4 bytes

            *m.old_message_ids,				# ?Q - ? x 8 bytes
            ips)					# ?s - ? x 4 bytes

    if isinstance(m, OldRequestMessage):
        return pack(
            "!BQ",
            MessageType.OLD_REQUEST,			# B - 1 byte
            m.uniq_msg_id)				# Q - 8 bytes

    if isinstance(m, OldReplyMessage):
        sender_nick = m.sender_nick.encode()
        msg_text = m.msg_text.encode()
        return pack(
            "!BQLL"
                f"{len(sender_nick)}s"
                f"{len(msg_text)}s",
            MessageType.OLD_REPLY,			# B - 1 byte
            m.uniq_msg_id,				# Q - 8 bytes
            len(sender_nick),				# L - 4 bytes
            len(msg_text),				# L - 4 bytes

            sender_nick,				# ?s - ? chars (bytes)
            msg_text)					# ?s - ? * chars

    dprint("ERROR: message type not implemented")
    return None




def unpack_chat_relay_message(data: bytes):
    """ unpacker for chat relay messages """
    (_,				# B - 1 byte
        uniq_msg_id,		# Q - 8 bytes
        sender_ip,		# L - 4 bytes
        old_msgs_length,	# L - 4 bytes
        nick_length,		# L - 4 bytes
        msg_length) = (		# L - 4 bytes
            unpack_from("!BQ4sLLL", data) )
    offset = 25

    old_message_ids = list( unpack_from(
            f"!{old_msgs_length}Q", data, offset=offset) )
    offset += 8 * old_msgs_length

    sender_nick = unpack_from(
            f"!{nick_length}s", data, offset=offset)[0].decode()
    offset += nick_length

    msg_text = unpack_from(
            f"!{msg_length}s", data, offset=offset)[0].decode()

    return ChatRelayMessage(
        uniq_msg_id = uniq_msg_id,
        sender_ip = IPv4Address(sender_ip),
        old_message_ids = old_message_ids,
        sender_nick = sender_nick,
        msg_text = msg_text)



def unpack_joinleave_relay_message(data: bytes):
    """ unpacker for join/leave relay messages """
    (msg_type,			# B - 1 byte
        uniq_msg_id,		# Q - 8 bytes
        sender_ip,		# L - 4 bytes
        old_msgs_length,	# L - 4 bytes
        nick_length) = (	# L - 4 bytes
            unpack_from("!BQLLL", data) )
    offset = 21

    old_message_ids = list( unpack_from(
            f"!{old_msgs_length}Q", data, offset=offset) )
    offset += 8 * old_msgs_length

    sender_nick = unpack_from(
            f"!{nick_length}s", data, offset=offset)[0].decode()

    if msg_type == MessageType.JOIN_RELAY:
        ret_type = JoinRelayMessage
    else:
        ret_type = LeaveRelayMessage

    return ret_type(
        uniq_msg_id = uniq_msg_id,
        sender_ip = IPv4Address(sender_ip),
        old_message_ids = old_message_ids,
        sender_nick = sender_nick)


def unpack_join_request_message(data: bytes):
    """ unpacker for join request messages """
    (_,				# B - 1 byte
        uniq_msg_id,		# Q - 8 bytes
        nick_length) = (	# L - 4 bytes
            unpack_from("!BQL", data) )
    offset = 13

    sender_nick = unpack_from(
            f"!{nick_length}s", data, offset=offset)[0].decode()

    return JoinRequestMessage(
        uniq_msg_id = uniq_msg_id,
        sender_nick = sender_nick)


def unpack_join_reply_message(data: bytes):
    """ unpacker for chat relay messages """
    (_,				# B - 1 byte
        old_msgs_length,	# L - 4 bytes
        ip_addrs_length ) = (	# L - 4 bytes
            unpack_from("!BLL", data) )
    offset = 9

    old_message_ids = list( unpack_from(
            f"!{old_msgs_length}Q", data, offset=offset) )
    offset += 8 * old_msgs_length

    ip_addresses = list( map(IPv4Address, unpack_from(
            f"!{ip_addrs_length}L", data, offset=offset)) )

    return JoinReplyMessage(
        old_message_ids = old_message_ids,
        ip_addresses = ip_addresses)


def unpack_old_reply_message(data: bytes):
    """ unpacker for chat relay messages """
    (_,				# B - 1 byte
        uniq_msg_id,		# Q - 8 bytes
        nick_length,		# L - 4 bytes
        msg_length) = (		# L - 4 bytes
            unpack_from("!BQLL", data) )
    offset = 17

    sender_nick = unpack_from(
            f"!{nick_length}s", data, offset=offset)[0].decode()
    offset += nick_length

    msg_text = unpack_from(
            f"!{msg_length}s", data, offset=offset)[0].decode()

    return OldReplyMessage(
        uniq_msg_id = uniq_msg_id,
        sender_nick = sender_nick,
        msg_text = msg_text )


def unpacker(data: bytes):
    """ unpacker - unpacks messages from raw data """

    match unpack_from("!B", data)[0]:	# Unpacks message type

        case MessageType.CHAT_RELAY:
            return unpack_chat_relay_message(data)

        case MessageType.JOIN_RELAY | MessageType.LEAVE_RELAY:
            return unpack_joinleave_relay_message(data)

        case MessageType.KEEPALIVE_RELAY:
            (_,				# B - 1 byte
                uniq_msg_id,		# Q - 8 bytes
                sender_ip ) = (		# 4s - 4 bytes
                    unpack("!BQL", data) )
            return KeepaliveRelayMessage(
                uniq_msg_id = uniq_msg_id,
                sender_ip = IPv4Address(sender_ip))

        case MessageType.JOIN_REQUEST:
            return unpack_join_request_message(data)

        case MessageType.JOIN_REPLY:
            return unpack_join_reply_message(data)

        case MessageType.OLD_REQUEST:
            (_,				# B - 1 byte
                uniq_msg_id ) =	(	# Q - 8 bytes
                    unpack("!BQ", data) )
            return OldRequestMessage(
                uniq_msg_id = uniq_msg_id)

        case MessageType.OLD_REPLY:
            return unpack_old_reply_message(data)
