import unittest

from smplchat.message_list import (
    MessageList,
    MessageEntry )
from smplchat.message import (
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    JoinReplyMessage,
    JoinRequestMessage )

class TestMessageList(unittest.TestCase):
    def test_init(self):
        self.ml = MessageList()
    
    def add_chat1(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 3,
            sender_ip = 55,
            old_message_ids = [],
            sender_nick = "tester",
            msg_text = "testing yeah" ))

    def add_chat2(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 5,
            sender_ip = 73,
            old_message_ids = [],
            sender_nick = "tester2",
            msg_text = "testing hell yeah" ))

    def add_chat_with_history(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 55,
            sender_ip = 73,
            old_message_ids = [3,5],
            sender_nick = "hisory-person",
            msg_text = "history testing" ))

    def add_chat_with_history2(self):
        self.ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 81,
            sender_ip = 744,
            old_message_ids = [55],
            sender_nick = "hisory-person2",
            msg_text = "history of history testing" ))

    def add_join(self):
        self.ml.add(JoinRelayMessage(
            msg_type = 1,
            uniq_msg_id = 4,
            sender_ip = 62,
            old_message_ids = [],
            sender_nick = "joiner" ))

    def add_leave(self):
        self.ml.add(LeaveRelayMessage(
            msg_type = 2,
            uniq_msg_id = 9,
            sender_ip = 92,
            old_message_ids = [],
            sender_nick = "leaver" ))

    def add_join_reply(self):
        self.ml.add(JoinReplyMessage(
            msg_type = 129,
            old_message_ids = [3,5,9],
            ip_addresses = [0,1,2] ))

    def add_join_request(self):
        self.ml.add(JoinRequestMessage(
            msg_type = 128,
            uniq_msg_id = 23579,
            sender_nick = "hei_vaan" ))

    def test_add(self):
        self.ml = MessageList()
        self.add_chat1()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, mtype=0, seen=1,
            nick='tester', message='testing yeah') ])

    def test_addmore(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat2()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, mtype=0, seen=1,
            nick='tester', message='testing yeah'),
            MessageEntry( uid=5, mtype=0, seen=1,
            nick='tester2', message='testing hell yeah'),
             ])

    def test_joinleave(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat2()
        self.add_join()
        self.add_leave()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, mtype=0, seen=1,
            nick='tester', message='testing yeah'),
            MessageEntry( uid=5, mtype=0, seen=1,
            nick='tester2', message='testing hell yeah'),
            MessageEntry(uid=4, mtype=1, seen=1,
            nick='joiner', message='*** joined the chat'),
            MessageEntry(uid=9, mtype=2, seen=1,
            nick='leaver', message='*** left the chat') ])

    def test_history_add(self):
        self.ml = MessageList()
        self.add_chat_with_history()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, mtype=-1, seen=0,
            nick='system', message='<3> message pending'),
            MessageEntry( uid=5, mtype=-1, seen=0,
            nick='system', message='<5> message pending'),
            MessageEntry(uid=55, mtype=0, seen=1,
            nick='hisory-person', message='history testing')])

    def test_history_filled(self):
        self.ml = MessageList()
        self.add_chat_with_history()
        self.add_chat1()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, mtype=0, seen=1,
            nick='tester', message='testing yeah'),
            MessageEntry( uid=5, mtype=-1, seen=0,
            nick='system', message='<5> message pending'),
            MessageEntry(uid=55, mtype=0, seen=1,
            nick='hisory-person', message='history testing')])

    def test_history_of_history_filled(self):
        self.ml = MessageList()
        self.add_chat_with_history2()
        self.add_chat_with_history()
        self.add_chat2()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, mtype=-1, seen=0,
            nick='system', message='<3> message pending'),
            MessageEntry( uid=5, mtype=0, seen=1,
            nick='tester2', message='testing hell yeah'),
            MessageEntry(uid=55, mtype=0, seen=1,
            nick='hisory-person', message='history testing'),
            MessageEntry(uid=81, mtype=0, seen=1,
            nick='hisory-person2', message='history of history testing')])

    def test_seen_counter(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat1()
        self.add_chat1()
        self.assertEqual(self.ml.get(), [
            MessageEntry( uid=3, mtype=0, seen=3,
            nick='tester', message='testing yeah') ])

    def test_join_reply(self):
        self.ml = MessageList()
        self.add_join_reply()
        self.assertEqual( [ str(x.message) for x in self.ml.get() ],
            [ str(x.message) for x in [
                MessageEntry( uid=3, mtype=-1, seen=0,
                nick='system', message='<3> message pending'),
                MessageEntry(uid=5, mtype=-1, seen=0,
                nick='system', message='<5> message pending'),
                MessageEntry(uid=9, mtype=-1, seen=0,
                nick='system', message='<9> message pending'),
                MessageEntry(uid=0, mtype=1, seen=1,
                nick='system', message='*** Join request succesful') ] ] )

    def test_unsupported(self):
        self.ml = MessageList()
        self.add_join_request()
        self.assertEqual(self.ml.get(), [] )

    def test_sys_message(self):
        self.ml = MessageList()
        self.ml.sys_message("joopajoo")
        self.assertEqual(self.ml.get()[0].message, "joopajoo")
        self.assertEqual(self.ml.get()[0].nick, "system")
