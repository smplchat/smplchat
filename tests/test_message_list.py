import unittest
from ipaddress import IPv4Address
from smplchat.settings import MAX_MESSAGES
from smplchat.message_list import MessageList
from smplchat.message import (
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    JoinReplyMessage,
    JoinRequestMessage,
    OldReplyMessage,
    KeepaliveRelayMessage)
from smplchat.message_list.list import (
    FullMessageEntry,
    WaitingMessageEntry,
    SystemMessageEntry)


class TestMessageList(unittest.TestCase):
    def test_init(self):
        self.ml = MessageList()

    def add_chat1(self):
        self.ml.add(ChatRelayMessage(
            uniq_msg_id=3,
            sender_ip=55,
            old_message_ids=[],
            sender_nick="tester",
            msg_text="testing yeah"))

    def add_chat2(self):
        self.ml.add(ChatRelayMessage(
            uniq_msg_id=5,
            sender_ip=73,
            old_message_ids=[],
            sender_nick="tester2",
            msg_text="testing hell yeah"))

    def add_chat3(self):
        self.ml.add(ChatRelayMessage(
            uniq_msg_id=5,
            sender_ip=73,
            old_message_ids=[13],
            sender_nick="mokkeli",
            msg_text="höh. ei se nyt niin saa olla."))

    def add_chat_with_history(self):
        self.ml.add(ChatRelayMessage(
            uniq_msg_id=55,
            sender_ip=73,
            old_message_ids=[3, 5],
            sender_nick="hisory-person",
            msg_text="history testing"))

    def add_chat_with_history2(self):
        self.ml.add(ChatRelayMessage(
            uniq_msg_id=81,
            sender_ip=744,
            old_message_ids=[55],
            sender_nick="hisory-person2",
            msg_text="history of history testing"))

    def add_join(self):
        self.ml.add(JoinRelayMessage(
            uniq_msg_id=4,
            sender_ip=62,
            old_message_ids=[],
            sender_nick="joiner"))

    def add_leave(self):
        self.ml.add(LeaveRelayMessage(
            uniq_msg_id=9,
            sender_ip=92,
            old_message_ids=[],
            sender_nick="leaver"))

    def add_join_reply(self):
        self.ml.add(JoinReplyMessage(
            old_message_ids=[3, 5, 9],
            ip_addresses=[0, 1, 2]))

    def add_join_request(self):
        self.ml.add(JoinRequestMessage(
            uniq_msg_id=23579,
            sender_nick="hei_vaan"))

    def add_old_reply(self):
        self.ml.add(OldReplyMessage(
            uniq_msg_id=13,
            sender_nick="vastaamo",
            msg_text="sitä saa mitä kysyy"))

    def add_keepalive(self, uid=999):
        self.ml.add(KeepaliveRelayMessage(
            uniq_msg_id=uid,
            sender_ip=IPv4Address("22.2.2.2")))

    def test_add(self):
        self.ml = MessageList()
        self.add_chat1()
        self.assertEqual(self.ml.get(), [
            FullMessageEntry(uid=3, seen=1,
                         nick='tester', message='testing yeah')])

    def test_addmore(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat2()
        self.assertEqual(self.ml.get(), [
            FullMessageEntry(uid=3, seen=1,
                         nick='tester', message='testing yeah'),
            FullMessageEntry(uid=5, seen=1,
                         nick='tester2', message='testing hell yeah'),
        ])

    def test_joinleave(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat2()
        self.add_join()
        self.add_leave()
        self.assertEqual(self.ml.get(), [
            FullMessageEntry(uid=3, seen=1,
                             nick='tester', message='testing yeah'),
            FullMessageEntry(uid=5, seen=1,
                             nick='tester2', message='testing hell yeah'),
            FullMessageEntry(uid=4, seen=1,
                             nick='joiner', message='*** joined the chat'),
            FullMessageEntry(uid=9, seen=1,
                             nick='leaver', message='*** left the chat')])

    def test_history_add(self):
        self.ml = MessageList()
        self.add_chat_with_history()

        get = self.ml.get()
        self.assertIsInstance(get[0], WaitingMessageEntry)
        self.assertEqual(get[0].uid,3)
        self.assertIsInstance(get[1], WaitingMessageEntry)
        self.assertEqual(get[1].uid, 5)
        self.assertIsInstance(get[2], FullMessageEntry)
        self.assertEqual(get[2].message, "history testing")

    def test_history_filled(self):
        self.ml = MessageList()
        self.add_chat_with_history()
        self.add_chat1()

        get = self.ml.get()
        self.assertIsInstance(get[0], FullMessageEntry)
        self.assertEqual(get[0].message, "testing yeah")
        self.assertIsInstance(get[1], WaitingMessageEntry)
        self.assertEqual(get[1].uid, 5)
        self.assertIsInstance(get[2], FullMessageEntry)
        self.assertEqual(get[2].message, "history testing")

    def test_history_of_history_filled(self):
        self.ml = MessageList()
        self.add_chat_with_history2()
        self.add_chat_with_history()
        self.add_chat2()
        get = self.ml.get()
        self.assertIsInstance(get[0], WaitingMessageEntry)
        self.assertEqual(get[0].uid, 3)
        self.assertIsInstance(get[1], FullMessageEntry)
        self.assertEqual(get[1].message, "testing hell yeah")
        self.assertIsInstance(get[2], FullMessageEntry)
        self.assertEqual(get[2].message, "history testing")
        self.assertIsInstance(get[3], FullMessageEntry)
        self.assertEqual(get[3].message, "history of history testing")

    def test_seen_counter(self):
        self.ml = MessageList()
        self.add_chat1()
        self.add_chat1()
        self.add_chat1()
        self.assertEqual(self.ml.get(), [
            FullMessageEntry(uid=3, seen=3,
                             nick='tester', message='testing yeah')])

    def test_join_reply(self):
        self.ml = MessageList()
        self.add_join_reply()

        for i, num in enumerate((3, 5, 9)):
            self.assertEqual(self.ml.get()[i].uid, num)
            self.assertIsInstance(self.ml.get()[i], WaitingMessageEntry)

        self.assertEqual(self.ml.get()[3].message, '*** Join request successful')
        self.assertIsInstance(self.ml.get()[3], SystemMessageEntry)

    def test_unsupported(self):
        self.ml = MessageList()
        self.add_join_request()
        self.assertEqual(self.ml.get(), [])

    def test_sys_message(self):
        self.ml = MessageList()
        self.ml.sys_message("joopajoo")
        self.assertEqual(self.ml.get()[0].message, "joopajoo")
        self.assertIn("System", self.ml.get_textual_contents()[0])

    def test_old_reply(self):
        self.ml = MessageList()
        self.add_chat3()
        self.add_old_reply()
        self.assertEqual(self.ml.get(), [
            FullMessageEntry(uid=13, seen=1,
                             nick='vastaamo', message='sitä saa mitä kysyy'),
            FullMessageEntry(uid=5, seen=1,
                             nick='mokkeli', message='höh. ei se nyt niin saa olla.')])

    def test_old_reply_no_request(self):
        self.ml = MessageList()
        self.add_old_reply()
        self.assertEqual(self.ml.get(), [])

    def test_cleanup(self):
        ml = MessageList()
        for i in range(MAX_MESSAGES + 10):
            ml._MessageList__messages.append(
                FullMessageEntry(uid=i, seen=1, nick="n", message="m")
            )
        ml.cleanup()
        self.assertEqual(len(ml.get()), MAX_MESSAGES)
        self.assertEqual(ml.get()[0].uid, 10)
        self.assertEqual(ml.get()[-1].uid, MAX_MESSAGES + 9)
