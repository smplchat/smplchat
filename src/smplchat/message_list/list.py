""" list - Provides message list and methods to manipulate it """
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import TypeAlias, List

from smplchat.message import (
    MessageType,
    Message,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    JoinReplyMessage,
    OldReplyMessage,
    KeepaliveRelayMessage)
from smplchat.utils import (
    dprint, get_time_from_uid)


@dataclass
class FullMessageEntry:
    """ Entry in the message list
    
        Details:
        uid - unique ID of message
        mtype - type of message
        seen - counter how many times message is added
        nick - the nick of sender
        message - message content
    """
    uid: int
    mtype: int
    seen: int
    nick: str
    message: str


@dataclass
class WaitingMessageEntry:
    uid: int
    fetch_count: int
    last_tried: datetime

@dataclass
class KeepaliveMessageEntry:
    uid: int
    seen: int


@dataclass
class GivenUpMessageEntry:
    uid: int


@dataclass
class SystemMessageEntry:
    message: str
    timestamp: datetime


MessageEntry: TypeAlias = FullMessageEntry | WaitingMessageEntry | GivenUpMessageEntry | SystemMessageEntry | KeepaliveMessageEntry


class MessageList:
    """ MessageList - The class for the list. """
    def __init__(self):
        self.__messages: List[MessageEntry] = []
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
                self.__messages.insert(pos, WaitingMessageEntry(rcv_uid, 0, datetime.now()))
                pos += 1
                new_entries = True
        return new_entries


    def __update_message(self, uid, mtype, nick, message):
        pos = self.find(uid)
        if pos is not None:
            entry = self.__messages[pos]

            if isinstance(entry, (WaitingMessageEntry, GivenUpMessageEntry)):
                self.__messages[pos] = self.__messages[pos] = FullMessageEntry(
                    uid=uid,
                    mtype=mtype,
                    seen=1,
                    nick=nick,
                    message=message)
                self.updated = True
                return True
            if isinstance(entry, FullMessageEntry):
                seen = entry.seen
                self.__messages[pos] = FullMessageEntry(
                    uid=entry.uid,
                    mtype=mtype,
                    seen=seen + 1,
                    nick=entry.nick,
                    message=entry.message)
                return True
            if isinstance(entry, KeepaliveMessageEntry):
                seen = entry.seen
                self.__messages[pos] = KeepaliveMessageEntry(
                    uid=entry.uid,
                    seen=seen + 1)
                return True
        return False

    def __generate_message(self, msg_type, text):
        """ generates message to be diplayed according message type """
        match msg_type:
            case MessageType.CHAT_RELAY:
                return text
            case MessageType.JOIN_RELAY:
                return "*** joined the chat"
            case MessageType.LEAVE_RELAY:
                return "*** left the chat"
        return ""

    def add(self, msg: Message):
        """ add - Adds message and its history to the list """
        if isinstance(msg, (ChatRelayMessage, JoinRelayMessage,
                LeaveRelayMessage, OldReplyMessage)):
            uid = msg.uniq_msg_id
            nick = msg.sender_nick
            mtype = ( msg.old_msg_type if hasattr(msg, "old_msg_type")
                    else msg.msg_type )
            text = msg.msg_text if hasattr(msg, "msg_text") else ""
            message = self.__generate_message(mtype, text)

            if self.__update_message(uid, mtype, nick, message):
                if hasattr(msg, "old_message_ids"):
                    self.__add_unseen_history(uid, msg.old_message_ids)
                return True

            if isinstance(msg, OldReplyMessage):
                dprint("Got reply without asking")
                return False

            self.__messages.append(FullMessageEntry(
                uid=uid,
                mtype=mtype,
                seen=1,
                nick=nick,
                message=message))
            if hasattr(msg, "old_message_ids"):
                self.__add_unseen_history(uid, msg.old_message_ids)
            self.updated = True
            return True

        if isinstance(msg, JoinReplyMessage):
            waiting_for = map(lambda x: WaitingMessageEntry(uid=x, last_tried=datetime.now(), fetch_count=0),
                              msg.old_message_ids)
            self.__messages += waiting_for
            self.sys_message("*** Join request successful")
            self.updated = True
            return True

        if isinstance(msg, KeepaliveRelayMessage):
            # check if we have the uid already
            pos = self.find(msg.uniq_msg_id)
            if pos is not None and isinstance(self.__messages[pos], KeepaliveMessageEntry):
                self.__messages[pos].seen += 1
                return True
            # if new, add
            self.__messages.append(KeepaliveMessageEntry(
                uid=msg.uniq_msg_id, seen=1 ))
            return True

        dprint("ERROR: Message type is not supported by MessagList")
        dprint(msg)
        return False

    def sys_message(self, text):
        """ Appends system message to the end of message list"""
        self.__messages.append(SystemMessageEntry(message=text, timestamp=datetime.now()))
        self.updated = True

    def find(self, uid: int):
        """ find - finds if there is already message of uid
            returns position in the list or None
        """
        for i, entry in enumerate(self.__messages):
            if hasattr(entry, "uid") and entry.uid == uid:
                return i
        return None

    def is_seen(self, uid: int):
        """ is_seen - Returns how many times uid is seen """
        for m in self.__messages:
            if isinstance(m, (FullMessageEntry, KeepaliveMessageEntry)) and m.uid == uid:
                return m.seen
            if isinstance(m, (WaitingMessageEntry, GivenUpMessageEntry)) and m.uid == uid:
                return 0
        return None

    def get(self):
        """ get - Gets current list """
        self.__update()
        return self.__messages

    def latest_ids(self, limit=None):
        """Returns latest IDs and has a limit function."""
        uid_list = [x.uid for x in self.__messages if isinstance(x, FullMessageEntry)]
        if limit is None or limit >= len(uid_list):
            return uid_list
        return uid_list[-limit:]

    def get_waiting_message(self) -> int | None:
        def __can_be_requested(item: tuple[int, MessageEntry]):
            msg = item[1]
            if not isinstance(msg, WaitingMessageEntry):
                return False
            return msg.last_tried < (datetime.now() - timedelta(seconds=1))

        e = enumerate(self.__messages)
        waiting_messages: list[tuple[int, WaitingMessageEntry]] = list(filter(__can_be_requested, e))
        if not waiting_messages:
            return None
        last = waiting_messages[-1]
        last_index = last[0]
        last_msg = last[1]
        if last_msg.fetch_count >= 4:
            self.__messages[last_index] = GivenUpMessageEntry(last_msg.uid)
        else:
            self.__messages[last_index] = WaitingMessageEntry(
                    uid=last_msg.uid,
                    fetch_count=last_msg.fetch_count + 1,
                    last_tried=datetime.now() )
        self.updated = True
        return last_msg.uid

    def get_textual_contents(self) -> list[str]:
        def __message_to_string(msg: MessageEntry) -> str:
            if isinstance(msg, FullMessageEntry):
                time_str = (datetime
                            .fromtimestamp(get_time_from_uid(msg.uid))
                            .strftime("%H:%M:%S"))
                return f"[{time_str}] {msg.nick}: {msg.message}"
            if isinstance(msg, WaitingMessageEntry):
                return "Message pending"
            if isinstance(msg, GivenUpMessageEntry):
                return "Failed to fetch message"
            if isinstance(msg, SystemMessageEntry):
                time_str = (msg.timestamp.strftime("%H:%M:%S"))
                return f"[{time_str}] [System] {msg.message}"
            return None
        
        return [ x for x in map(__message_to_string, self.__messages) if x ]

    def get_by_uid(self, uid: int) -> FullMessageEntry | None:
        for entry in self.__messages:
            if isinstance(entry, FullMessageEntry) and entry.uid == uid:
                return entry
        return None
