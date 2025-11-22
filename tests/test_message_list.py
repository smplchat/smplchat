import unittest

from smplchat.message_list import MessageList, MessageEntry
from smplchat.packet_mangler import (
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage )

class TestMessageList(unittest.TestCase):
    def test_init(self):
        self.ml = MessageList()
    
    def add_chat1(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 3,
            sender_ip = 55,
            sender_local_time = 666,
            old_message_ids = [],
            sender_nick = "tester",
            msg_text = "testing yeah" ))

    def add_chat2(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 5,
            sender_ip = 73,
            sender_local_time = 777,
            old_message_ids = [],
            sender_nick = "tester2",
            msg_text = "testing hell yeah" ))

    def add_chat_with_history(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 55,
            sender_ip = 73,
            sender_local_time = 777,
            old_message_ids = [3,5],
            sender_nick = "hisory-person",
            msg_text = "history testing" ))

    def add_chat_with_history2(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 81,
            sender_ip = 744,
            sender_local_time = 774,
            old_message_ids = [55],
            sender_nick = "hisory-person2",
            msg_text = "history of history testing" ))

    def add_join(self):
        self.ml.add(JoinRelayMessage(
            msg_type = 1,
            uniq_msg_id = 4,
            sender_ip = 62,
            sender_local_time = 7334,
            old_message_ids = [],
            sender_nick = "joiner" ))

    def add_leave(self):
        self.ml.add(LeaveRelayMessage(
            msg_type = 2,
            uniq_msg_id = 9,
            sender_ip = 92,
            sender_local_time = 2346,
            old_message_ids = [],
            sender_nick = "leaver" ))


    def test_add(self):
        self.ml = MessageList()
        self.add_chat1()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, seen=1, time=666,
            nick='tester', message='testing yeah') ])

    def test_addmore(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat2()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, seen=1, time=666,
            nick='tester', message='testing yeah'),
            MessageEntry( uid=5, seen=1, time=777,
            nick='tester2', message='testing hell yeah'),
             ])

    def test_joinleave(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat2()
        self.add_join()
        self.add_leave()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, seen=1, time=666,
            nick='tester', message='testing yeah'),
            MessageEntry( uid=5, seen=1, time=777,
            nick='tester2', message='testing hell yeah'),
            MessageEntry(uid=4, seen=1, time=7334,
            nick='joiner', message='*** joined the chat'),
            MessageEntry(uid=9, seen=1, time=2346,
            nick='leaver', message='*** left the chat') ])

    def test_history_add(self):
        self.ml = MessageList()
        self.add_chat_with_history()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, seen=0, time=0,
            nick='system', message='<3> message pending'),
            MessageEntry( uid=5, seen=0, time=0,
            nick='system', message='<5> message pending'),
            MessageEntry(uid=55, seen=1, time=777,
            nick='hisory-person', message='history testing')])

    def test_history_filled(self):
        self.ml = MessageList()
        self.add_chat_with_history()
        self.add_chat1()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, seen=1, time=666,
            nick='tester', message='testing yeah'),
            MessageEntry( uid=5, seen=0, time=0,
            nick='system', message='<5> message pending'),
            MessageEntry(uid=55, seen=1, time=777,
            nick='hisory-person', message='history testing')])

    def test_history_of_history_filled(self):
        self.ml = MessageList()
        self.add_chat_with_history2()
        self.add_chat_with_history()
        self.add_chat2()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, seen=0, time=0,
            nick='system', message='<3> message pending'),
            MessageEntry( uid=5, seen=1, time=777,
            nick='tester2', message='testing hell yeah'),
            MessageEntry(uid=55, seen=1, time=777,
            nick='hisory-person', message='history testing'),
            MessageEntry(uid=81, seen=1, time=774,
            nick='hisory-person2', message='history of history testing')])
