""" smplchat.message_gen - functions to generate messages """
from smplchat.utils import generate_uid
from .message import ChatRelayMessage

def new_message(nick, text, ip, msg_list):
    """ Generates new message. TODO: move this in better place """
    uid = generate_uid()
    return ChatRelayMessage(
        msg_type = 0,
        uniq_msg_id = uid,
        sender_ip = ip,
        old_message_ids = [], #msg_list.get_latest_uids(),
        sender_nick = nick,
        msg_text = text)
