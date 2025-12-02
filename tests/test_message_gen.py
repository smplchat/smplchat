import unittest
from ipaddress import IPv4Address
from unittest.mock import Mock

from smplchat.message import message_gen
from smplchat.message import (
    MessageType,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    KeepaliveRelayMessage,
    JoinRequestMessage,
    JoinReplyMessage,
    OldRequestMessage,
    OldReplyMessage
)

class TestMessageGen(unittest.TestCase):

    def test_chat_relay(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=10):
            mock_msg_list = Mock()
            mock_msg_list.latest_ids.return_value = [1, 2, 3]

            msg = message_gen.new_message(
                MessageType.CHAT_RELAY,
                ip=IPv4Address("1.0.1.1"),
                msg_list=mock_msg_list,
                nick="bulla",
                text="terve"
            )

            self.assertIsInstance(msg, ChatRelayMessage)
            self.assertEqual(msg.msg_type, MessageType.CHAT_RELAY)
            self.assertEqual(msg.msg_type, 0)
            self.assertEqual(msg.uniq_msg_id, 10)
            self.assertEqual(msg.sender_ip, IPv4Address("1.0.1.1"))
            self.assertEqual(msg.old_message_ids, [1, 2, 3])
            self.assertEqual(msg.sender_nick, "bulla")
            self.assertEqual(msg.msg_text, "terve")

    def test_chat_relay_missing_ip_nick(self):
        mock_msg_list = Mock()
        mock_msg_list.latest_ids.return_value = []

        # no ip
        with self.assertRaises(KeyError):
            message_gen.new_message(
                MessageType.CHAT_RELAY,
                msg_list=mock_msg_list,
                nick="n",
                text="t"
            )

        # no nick
        with self.assertRaises(KeyError):
            message_gen.new_message(
                MessageType.CHAT_RELAY,
                ip=IPv4Address("1.0.1.1"),
                msg_list=mock_msg_list,
                text="t"
            )

    def test_join_relay(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=42):
            mock_msg_list = Mock()
            mock_msg_list.latest_ids.return_value = [10, 20, 30]

            msg = message_gen.new_message(
                MessageType.JOIN_RELAY,
                ip=IPv4Address("5.4.2.1"),
                msg_list=mock_msg_list,
                nick="anon"
            )

            self.assertIsInstance(msg, JoinRelayMessage)
            self.assertEqual(msg.msg_type, MessageType.JOIN_RELAY)
            self.assertEqual(msg.msg_type, 1)
            self.assertEqual(msg.uniq_msg_id, 42)
            self.assertEqual(msg.sender_ip, IPv4Address("5.4.2.1"))
            self.assertEqual(msg.old_message_ids, [10, 20, 30])
            self.assertEqual(msg.sender_nick, "anon")

    def test_join_relay_missing_nick(self):
        mock_msg_list = Mock()
        mock_msg_list.latest_ids.return_value = []

        # no nick
        with self.assertRaises(KeyError):
            message_gen.new_message(
                MessageType.JOIN_RELAY,
                ip=IPv4Address("5.4.2.1"),
                msg_list=mock_msg_list
            )

    def test_leave_relay(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=69):
            mock_msg_list = Mock()
            mock_msg_list.latest_ids.return_value = [5, 15, 25]

            msg = message_gen.new_message(
                MessageType.LEAVE_RELAY,
                ip=IPv4Address("4.3.3.4"),
                msg_list=mock_msg_list,
                nick="tuutti"
            )

            self.assertIsInstance(msg, LeaveRelayMessage)
            self.assertEqual(msg.msg_type, MessageType.LEAVE_RELAY)
            self.assertEqual(msg.msg_type, 2)
            self.assertEqual(msg.uniq_msg_id, 69)
            self.assertEqual(msg.sender_ip, IPv4Address("4.3.3.4"))
            self.assertEqual(msg.old_message_ids, [5, 15, 25])
            self.assertEqual(msg.sender_nick, "tuutti")

    def test_leave_relay_missing_ip(self):
        mock_msg_list = Mock()
        mock_msg_list.latest_ids.return_value = []

        # no ip
        with self.assertRaises(KeyError):
            message_gen.new_message(
                MessageType.LEAVE_RELAY,
                msg_list=mock_msg_list,
                nick="tuutti"
            )

    def test_keepalive(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=666):
            msg = message_gen.new_message(MessageType.KEEPALIVE_RELAY, ip=IPv4Address("11.1.1.1"))

            self.assertIsInstance(msg, KeepaliveRelayMessage)
            self.assertEqual(msg.msg_type, MessageType.KEEPALIVE_RELAY)
            self.assertEqual(msg.msg_type, 3)
            self.assertEqual(msg.uniq_msg_id, 666)
            self.assertEqual(msg.sender_ip, IPv4Address("11.1.1.1"))

    def test_keepalive_missing_ip(self):
        with self.assertRaises(KeyError):
            message_gen.new_message(MessageType.KEEPALIVE_RELAY)

    def test_join_request(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=600):
            msg = message_gen.new_message(
                MessageType.JOIN_REQUEST,
                nick="saunis"
            )

            self.assertIsInstance(msg, JoinRequestMessage)
            self.assertEqual(msg.msg_type, MessageType.JOIN_REQUEST)
            self.assertEqual(msg.msg_type, 128)
            self.assertEqual(msg.uniq_msg_id, 600)
            self.assertEqual(msg.sender_nick, "saunis")

    def test_join_request_missing_nick(self):
        with self.assertRaises(KeyError):
            message_gen.new_message(MessageType.JOIN_REQUEST)

    def test_join_reply(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=67):
            mock_msg_list = Mock()
            mock_msg_list.latest_ids.return_value = [1, 2, 3, 4, 5]

            mock_client_list = Mock()
            mock_client_list.get.return_value = [
                IPv4Address("10.0.0.1"),
                IPv4Address("10.0.0.2"),
                IPv4Address("10.0.0.3")
            ]

            msg = message_gen.new_message(
                MessageType.JOIN_REPLY,
                msg_list=mock_msg_list,
                client_list=mock_client_list
            )

            self.assertIsInstance(msg, JoinReplyMessage)
            self.assertEqual(msg.msg_type, MessageType.JOIN_REPLY)
            self.assertEqual(msg.msg_type, 129)
            self.assertEqual(msg.old_message_ids, [1, 2, 3, 4, 5])
            self.assertEqual(msg.ip_addresses, [
                IPv4Address("10.0.0.1"),
                IPv4Address("10.0.0.2"),
                IPv4Address("10.0.0.3")
            ])

            mock_msg_list.latest_ids.assert_called_once_with(limit=100)

    def test_join_reply_missing_parameters(self):
        mock_msg_list = Mock()
        mock_msg_list.latest_ids.return_value = []

        # no client list
        with self.assertRaises(KeyError):
            message_gen.new_message(
                MessageType.JOIN_REPLY,
                msg_list=mock_msg_list
            )

    def test_old_request(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=7):
            msg = message_gen.new_message(
                MessageType.OLD_REQUEST,
                uid=44444
            )

            self.assertIsInstance(msg, OldRequestMessage)
            self.assertEqual(msg.msg_type, MessageType.OLD_REQUEST)
            self.assertEqual(msg.msg_type, 130)
            self.assertEqual(msg.uniq_msg_id, 44444)

    def test_old_request_missing_uid(self):
        with self.assertRaises(KeyError):
            message_gen.new_message(MessageType.OLD_REQUEST)

    def test_old_reply(self):
        with unittest.mock.patch.object(message_gen, "generate_uid", return_value=999):
            msg = message_gen.new_message(
                MessageType.OLD_REPLY,
                old_type=MessageType.CHAT_RELAY,
                uid=55,
                nick="parta",
                text="Punainen vai sininen!?"
            )

            self.assertIsInstance(msg, OldReplyMessage)
            self.assertEqual(msg.msg_type, MessageType.OLD_REPLY)
            self.assertEqual(msg.msg_type, 131)
            self.assertEqual(msg.old_msg_type, MessageType.CHAT_RELAY)
            self.assertEqual(msg.old_msg_type, 0)
            self.assertEqual(msg.uniq_msg_id, 55)
            self.assertEqual(msg.sender_nick, "parta")
            self.assertEqual(msg.msg_text, "Punainen vai sininen!?")

    def test_old_reply_missing_type_uid(self):

        # no type
        with self.assertRaises(KeyError):
            message_gen.new_message(
                MessageType.OLD_REPLY,
                uid=55,
                nick="huba",
                text="ttt"
            )

        # no uid
        with self.assertRaises(KeyError):
            message_gen.new_message(
                MessageType.OLD_REPLY,
                old_type=MessageType.CHAT_RELAY,
                nick="huba",
                text="ttt"
            )
