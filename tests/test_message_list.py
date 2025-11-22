import unittest

from smplchat.message_list import MessageList, MessageEntry
from smplchat.packet_mangler import ChatRelayMessage

class TestMessageList(unittest.TestCase):
    def test_init(self):
        ml = MessageList()

    def test_add(self):
        ml = MessageList()
        ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 3,
            sender_ip = 55,
            sender_local_time = 666,
            old_message_ids = [],
            sender_nick = "tester",
            msg_text = "testing yeah" ))
        self.assertEqual(ml.get(), [
            MessageEntry( uid=3, seen=1, time=666,
            nick='tester', message='testing yeah') ])
        return ml
            
    def test_addmore(self):
        ml = self.test_add()
        ml.add(ChatRelayMessage(
            msg_type = 0,
            uniq_msg_id = 5,
            sender_ip = 73,
            sender_local_time = 777,
            old_message_ids = [],
            sender_nick = "tester2",
            msg_text = "testing hell yeah" ))
        self.assertEqual(ml.get(), [
            MessageEntry( uid=3, seen=1, time=666,
            nick='tester', message='testing yeah'),
            MessageEntry( uid=5, seen=1, time=777,
            nick='tester2', message='testing hell yeah'),
             ])
        return ml
