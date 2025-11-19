import unittest
from random import randrange

from smplchat.packet_mangler import *

class TestPacker(unittest.TestCase):
    def test_chat_relay_message(self):
        for _ in range(200):
            tm = ChatRelayMessage(
                msg_type = MessageType.CHAT_RELAY,
                uniq_msg_id = randrange(0,99999999),
                sender_ip = randrange(0,99999999),
                sender_local_time = randrange(0,99999999),
                old_message_ids = ( [randrange(0,99999999)
                        for x in range(randrange(33))] ),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))),
                msg_text = "".join(chr(randrange(1,4000))
                        for x in range(randrange(2000))) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_join_relay_message(self):
        for _ in range(200):
            tm = JoinRelayMessage(
                msg_type = MessageType.JOIN_RELAY,
                uniq_msg_id = randrange(0,99999999),
                sender_ip = randrange(0,99999999),
                sender_local_time = randrange(0,99999999),
                old_message_ids = ( [randrange(0,99999999)
                        for x in range(randrange(33))] ),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_leave_relay_message(self):
        for _ in range(200):
            tm = LeaveRelayMessage(
                msg_type = MessageType.LEAVE_RELAY,
                uniq_msg_id = randrange(0,99999999),
                sender_ip = randrange(0,99999999),
                sender_local_time = randrange(0,99999999),
                old_message_ids = ( [randrange(0,99999999)
                        for x in range(randrange(33))] ),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_keepalive_relay_message(self):
        for _ in range(200):
            tm = KeepaliveRelayMessage(
                msg_type = MessageType.KEEPALIVE_RELAY,
                uniq_msg_id = randrange(0,99999999),
                sender_ip = randrange(0,99999999) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_join_request_message(self):
        for _ in range(200):
            tm = JoinRequestMessage(
                msg_type = MessageType.JOIN_REQUEST,
                uniq_msg_id = randrange(0,99999999),
                sender_local_time = randrange(0,99999999),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))) )
            self.assertEqual(tm, unpacker(packer(tm)))
