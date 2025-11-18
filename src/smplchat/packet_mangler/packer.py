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
            f"@BLLL20L32sLs{len(m.msg_text)}",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# L - 4 bytes
            m.sender_ip,		# L - 4 bytes
            m.sender_local_time,	# L - 4 bytes
            m.old_message_ids,		# 20L - 20x 4 bytes
            m.sender_nick,		# 32s - 32 chars (bytes)
            len(m.msg_text),		# L - 4 bytes
            m.msg_text)			# ?s - ? * chars

    if isinstance(m, JoinRelayMessage, LeaveRelayMessage):
        return pack(
            "@BLLL20L32s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# L - 4 bytes
            m.sender_ip,		# L - 4 bytes
            m.sender_local_time,	# L - 4 bytes
            m.old_message_ids,		# 20L - 20x 4 bytes
            m.sender_nick)		# 32s - 32 chars (bytes)

    if isinstance(m, KeepaliveRelayMessage):
        return pack(
            "@BLL",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# L - 4 bytes
            m.sender_ip)		# L - 4 bytes

    if isinstance(m, JoinRequestMessage):
        return pack(
            "@BLL32s",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id,		# L - 4 bytes
            m.sender_local_time,	# L - 4 bytes
            m.sender_nick)		# 32s - 32 chars (bytes)

    if isinstance(m, JoinReplyMessage):
        return pack(
            f"@BL100LLL{len(m.ip_addresses)}",
            m.msg_type,			# B - 1 byte
            m.old_message_ids,		# 100L - 100x 4 bytes
            len(m.ip_addresses),	# L - 4 bytes
            m.ip_addresses)		# ?L - ? x 4 bytes

    if isinstance(m, OldRequestMessage):
        return pack(
            "@BL",
            m.msg_type,			# B - 1 byte
            m.uniq_msg_id)		# L - 4 bytes

    if isinstance(m, OldReplyMessage):
        return pack(
            f"@BBLL32sLs{len(m.old_msg_text)}",
            m.msg_type,			# B - 1 byte
            m.old_msg_type,		# B - 1 byte
            m.old_msg_id,		# L - 4 bytes
            m.old_sender_local_time,	# L - 4 bytes
            m.old_sender_nick,		# 32s - 32 chars (bytes)
            len(m.old_msg_text),	# L - 4 bytes
            m.old_msg_text)		# ?s - ? * chars

    dprint("ERROR: message type not implemented")
    return None
