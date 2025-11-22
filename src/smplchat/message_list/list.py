""" list - Provides message list and methods to manipulate it """
from dataclasses import dataclass
from smplchat.packet_mangler import (
    Message,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    JoinReplyMessage)
from smplchat.utils import (
    generate_uid,
    get_time_from_uid,
    dprint )

@dataclass
class MessageEntry:
    """ Entry in the message list
    
        Details:
        uid - unique ID of message
        seen - counter how many times message is added
        time - senders local time
        nick - the nick of sender
        message - message content
    """
    uid: int
    seen: int
    time: int
    nick: str
    message: str

class MessageList:
    """ MessageList - The class for the list. """
    def __init__(self):
        self.__messages = []
        self.updated = False

    def __update(self):
        """ __update - internal command that for example cut too long list"""

    def __add_unseen_history(self, uid: int, history: list[int]):
        """ __add_unseen_history - adds unseen messages to
            the message list in corrent order and place. """
        pos = self.find(uid)
        new_entries = False
        # If this is not the first time we got the actual message
        if self.__messages[pos].seen != 1:
            return False
        for rcv_uid in history:
            if self.find(rcv_uid) is None:
                self.__messages.insert(pos, MessageEntry (
                    uid = rcv_uid,
                    seen = 0,
                    time = 0,
                    nick = "system",
                    message = f"<{rcv_uid}> message pending" ) )
                pos += 1
                new_entries = True
        return new_entries


    def __update_message(self, uid, time, nick, message):
        pos = self.find(uid)
        if pos is not None:
            entry = self.__messages[pos]
            seen = entry.seen
            if seen > 0:
                self.__messages[pos] = MessageEntry (
                    uid = entry.uid,
                    seen = seen + 1,
                    time = entry.time,
                    nick = entry.nick,
                    message = entry.message )
                return True
            self.__messages[pos] = MessageEntry (
                    uid = uid,
                    seen = 1,
                    time = time,
                    nick = nick,
                    message = message )
            self.updated = True
            return True
        return False

    def add(self, msg: Message):
        """ add - Adds message and its history to the list """
        if isinstance(msg,
                (ChatRelayMessage, JoinRelayMessage, LeaveRelayMessage)):
            uid = msg.uniq_msg_id
            time = msg.sender_local_time
            nick = msg.sender_nick
            if isinstance(msg, ChatRelayMessage):
                message = msg.msg_text
            elif isinstance(msg, JoinRelayMessage):
                message = "*** joined the chat"
            elif isinstance(msg, LeaveRelayMessage):
                message = "*** left the chat"
            if self.__update_message(uid, time, nick, message):
                self.__add_unseen_history(uid, msg.old_message_ids)
                return False

            self.__messages.append(MessageEntry (
                uid = uid,
                seen = 1,
                time = time,
                nick = nick,
                message = message ))

            self.__add_unseen_history(uid, msg.old_message_ids)
            self.updated = True
            return True

        if isinstance(msg, JoinReplyMessage):
            uid = generate_uid()
            self.__messages.append(MessageEntry (
                uid = uid,
                seen = 1,
                time = get_time_from_uid(uid),
                nick = "system",
                message = "*** Join request succesful"))
            self.__add_unseen_history(uid, msg.old_message_ids)
            self.updated = True
            return True

        dprint("ERROR: Message type is not supported by MessagList")
        dprint(msg)
        return False


    def find(self, uid: int):
        """ find - finds if there is already message of uid
            returns position in the list or None
        """
        for i, entry in enumerate(self.__messages):
            if entry.uid == uid:
                return i
        return None

    def get(self):
        """ get - Gets current list """
        self.__update()
        return self.__messages

    def latest_ids(self, limit=None):
        """Returns latest IDs and has a limit function."""
        if limit is None or limit >= len(self.__messages):
            base = self.__messages
        else:
            base = self.__messages[-limit:]
        return [entry.uid for entry in base]
