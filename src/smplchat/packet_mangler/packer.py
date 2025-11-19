""" smplchat.packet_mangler.packer - functions to form data from message classes """
from struct import pack, unpack, unpack_from
from smplchat.settings import dprint
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


def packer(m: Message):
    """ packer - packs message to binary data for sending """
    # pylint: disable-msg=too-many-return-statements, too-many-function-args

    if isinstance(m, ChatRelayMessage):
        sender_nick = m.sender_nick.encode()
        msg_text = m.msg_text.encode()
        return pack(
            "=BQLLLLL"
                f"{len(m.old_message_ids)}Q"
                f"{len(sender_nick)}s"
                f"{len(msg_text)}s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_ip,		# L - 4 bytes
            m.sender_local_time,	# L - 4 bytes
            len(m.old_message_ids),	# L - 4 bytes
            len(sender_nick),		# L - 4 bytes
            len(msg_text),		# L - 4 bytes

            *m.old_message_ids,		# ?Q - ? x 8 bytes
            sender_nick,		# ?s - ? chars (bytes)
            msg_text)			# ?s - ? * chars

    if isinstance(m, (JoinRelayMessage, LeaveRelayMessage)):
        sender_nick = m.sender_nick.encode()
        return pack(
            "=BQLLLL"
                f"{len(m.old_message_ids)}Q"
                f"{len(sender_nick)}s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_ip,		# L - 4 bytes
            m.sender_local_time,	# L - 4 bytes
            len(m.old_message_ids),	# L - 4 bytes
            len(sender_nick),		# L - 4 bytes

            *m.old_message_ids,		# ?Q - ?x 8 bytes
            sender_nick)		# ?s - ? chars (bytes)

    if isinstance(m, KeepaliveRelayMessage):
        return pack(
            "=BQL",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_ip)		# L - 4 bytes

    if isinstance(m, JoinRequestMessage):
        sender_nick = m.sender_nick.encode()
        return pack(
            "=BQLL"
                f"{len(sender_nick)}s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_local_time,	# L - 4 bytes
            len(sender_nick),		# L - 4 bytes

            sender_nick)		# ?s - ? chars (bytes)

    if isinstance(m, JoinReplyMessage):
        return pack(
            f"=B100QL{len(m.ip_addresses)}L",
            m.msg_type,			# B - 1 byte
            m.old_message_ids,		# 100Q - 100x 8 bytes
            len(m.ip_addresses),	# L - 4 bytes
            m.ip_addresses)		# ?L - ? x 4 bytes

    if isinstance(m, OldRequestMessage):
        return pack(
            "=BQ",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id)		# Q - 8 bytes

    if isinstance(m, OldReplyMessage):
        return pack(
            f"=BBQL32sL{len(m.old_msg_text)}s",
            m.msg_type,			# B - 1 byte
            m.old_msg_type,		# B - 1 byte
            m.old_msg_id,		# Q - 8 bytes
            m.old_sender_local_time,	# L - 4 bytes
            m.old_sender_nick,		# 32s - 32 chars (bytes)
            len(m.old_msg_text),	# L - 4 bytes
            m.old_msg_text)		# ?s - ? * chars

    dprint("ERROR: message type not implemented")
    return None




def unpack_chat_relay_message(data: bytes):
    """ unpacker for chat relay messages """
    (msg_type,			# B - 1 byte
        uniq_msg_id,		# Q - 8 bytes
        sender_ip,		# L - 4 bytes
        sender_local_time,	# L - 4 bytes
        old_msgs_length,	# L - 4 bytes
        nick_length,		# L - 4 bytes
        msg_length) = (		# L - 4 bytes
            unpack_from("=BQLLLLL", data) )
    offset = 29

    old_message_ids = list( unpack_from(
            f"={old_msgs_length}Q", data, offset=offset) )
    offset += 8 * old_msgs_length

    sender_nick = unpack_from(
            f"={nick_length}s", data, offset=offset)[0].decode()
    offset += nick_length

    msg_text = unpack_from(
            f"={msg_length}s", data, offset=offset)[0].decode()

    return ChatRelayMessage(
        msg_type = msg_type,
        uniq_msg_id = uniq_msg_id,
        sender_ip = sender_ip,
        sender_local_time = sender_local_time,
        old_message_ids = old_message_ids,
        sender_nick = sender_nick,
        msg_text = msg_text)



def unpack_joinleave_relay_message(data: bytes):
    """ unpacker for join/leave relay messages """
    (msg_type,			# B - 1 byte
        uniq_msg_id,		# Q - 8 bytes
        sender_ip,		# L - 4 bytes
        sender_local_time,	# L - 4 bytes
        old_msgs_length,	# L - 4 bytes
        nick_length) = (	# L - 4 bytes
            unpack_from("=BQLLLL", data) )
    offset = 25

    old_message_ids = list( unpack_from(
            f"={old_msgs_length}Q", data, offset=offset) )
    offset += 8 * old_msgs_length

    sender_nick = unpack_from(
            f"={nick_length}s", data, offset=offset)[0].decode()

    if msg_type == MessageType.JOIN_RELAY:
        ret_type = JoinRelayMessage
    else:
        ret_type = LeaveRelayMessage

    return ret_type(
        msg_type = msg_type,
        uniq_msg_id = uniq_msg_id,
        sender_ip = sender_ip,
        sender_local_time = sender_local_time,
        old_message_ids = old_message_ids,
        sender_nick = sender_nick)


def unpack_join_request_message(data: bytes):
    """ unpacker for join request messages """
    (msg_type,			# B - 1 byte
        uniq_msg_id,		# Q - 8 bytes
        sender_local_time,	# L - 4 bytes
        nick_length) = (	# L - 4 bytes
            unpack_from("=BQLL", data) )
    offset = 17

    sender_nick = unpack_from(
            f"={nick_length}s", data, offset=offset)[0].decode()

    return JoinRequestMessage(
        msg_type = msg_type,
        uniq_msg_id = uniq_msg_id,
        sender_local_time = sender_local_time,
        sender_nick = sender_nick)



def unpacker(data: bytes):
    """ unpacker - unpacks messages from raw data """
    # pylint: disable-msg=too-many-locals, too-many-return-statements

    match unpack_from("=B", data)[0]:	# Unpacks message type

        case MessageType.CHAT_RELAY:
            return unpack_chat_relay_message(data)

        case MessageType.JOIN_RELAY | MessageType.LEAVE_RELAY:
            return unpack_joinleave_relay_message(data)

        case MessageType.KEEPALIVE_RELAY:
            (msg_type,			# B - 1 byte
                uniq_msg_id,		# Q - 8 bytes
                sender_ip ) = (		# L - 4 bytes
                    unpack("=BQL", data) )
            return KeepaliveRelayMessage(
                msg_type = msg_type,
                uniq_msg_id = uniq_msg_id,
                sender_ip = sender_ip)

        case MessageType.JOIN_REQUEST:
            return unpack_join_request_message(data)

        case MessageType.JOIN_REPLY:
            ip_list_length = unpack_from("=L", data, offset=801)
            (msg_type,			# B - 1 byte
                old_message_ids,	# 100Q - 100x 8 bytes
                _,			# L - 4 bytes
                ip_addresses) =	(	# ?L - ? x 4 bytes
                    unpack(f"=B100QL{ip_list_length}L", data) )
            return JoinReplyMessage(
                msg_type = msg_type,
                old_message_ids = old_message_ids,
                ip_addresses = ip_addresses)

        case MessageType.OLD_REQUEST:
            (msg_type,			# B - 1 byte
                uniq_msg_id ) =	(	# Q - 8 bytes
                    unpack("=BQ", data) )
            return OldRequestMessage(
                msg_type = msg_type,
                uniq_msg_id = uniq_msg_id)

        case MessageType.OLD_REPLY:
            old_msg_length = unpack_from("=L", data, offset=46)
            ( msg_type,			# B - 1 byte
            old_msg_type,		# B - 1 byte
            old_msg_id,			# Q - 8 bytes
            old_sender_local_time,	# L - 4 bytes
            old_sender_nick,		# 32s - 32 chars (bytes)
            _,				# L - 4 bytes
            old_msg_text ) = (		# ?s - ? * chars
                unpack(f"=BBQL32sL{old_msg_length}s", data) )
            return OldReplyMessage(
                msg_type = msg_type,
                old_msg_type = old_msg_type,
                old_msg_id = old_msg_id,
                old_sender_local_time = old_sender_local_time,
                old_sender_nick = old_sender_nick,
                old_msg_text = old_msg_text )
