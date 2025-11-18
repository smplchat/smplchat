""" smplchat.packet_mangler.packer - functions to form data from message classes """
from struct import pack
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


def packer(m: Message):
    """ packer - packs message to binary data for sending """
    # pylint: disable-msg=too-many-return-statements, too-many-function-args

    if isinstance(m, ChatRelayMessage):
        return pack(
            f"@BQLL32Q32sL{len(m.msg_text)}s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_ip,		# L - 4 bytes
            m.sender_local_time,	# L - 4 bytes
            m.old_message_ids,		# 32Q - 32 x 8 bytes
            m.sender_nick,		# 32s - 32 chars (bytes)
            len(m.msg_text),		# L - 4 bytes
            m.msg_text)			# ?s - ? * chars

    if isinstance(m, JoinRelayMessage, LeaveRelayMessage):
        return pack(
            "@BQLL32Q32s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_ip,		# L - 4 bytes
            m.sender_local_time,	# L - 4 bytes
            m.old_message_ids,		# 32Q - 32x 8 bytes
            m.sender_nick)		# 32s - 32 chars (bytes)

    if isinstance(m, KeepaliveRelayMessage):
        return pack(
            "@BQL",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_ip)		# L - 4 bytes

    if isinstance(m, JoinRequestMessage):
        return pack(
            "@BQL32s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# Q - 8 bytes
            m.sender_local_time,	# L - 4 bytes
            m.sender_nick)		# 32s - 32 chars (bytes)

    if isinstance(m, JoinReplyMessage):
        return pack(
            f"@B100QL{len(m.ip_addresses)}L",
            m.msg_type,			# B - 1 byte
            m.old_message_ids,		# 100Q - 100x 8 bytes
            len(m.ip_addresses),	# L - 4 bytes
            m.ip_addresses)		# ?L - ? x 4 bytes

    if isinstance(m, OldRequestMessage):
        return pack(
            "@BQ",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id)		# Q - 8 bytes

    if isinstance(m, OldReplyMessage):
        return pack(
            f"@BBQL32sL{len(m.old_msg_text)}s",
            m.msg_type,			# B - 1 byte
            m.old_msg_type,		# B - 1 byte
            m.old_msg_id,		# Q - 8 bytes
            m.old_sender_local_time,	# L - 4 bytes
            m.old_sender_nick,		# 32s - 32 chars (bytes)
            len(m.old_msg_text),	# L - 4 bytes
            m.old_msg_text)		# ?s - ? * chars

    dprint("ERROR: message type not implemented")
    return None
