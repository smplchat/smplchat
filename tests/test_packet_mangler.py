import unittest
from random import randrange, choice
from ipaddress import IPv4Address
from secrets import randbits

from smplchat.udp_comms import packer, unpacker
from smplchat.message import *

class TestPacker(unittest.TestCase):
    def test_chat_relay_message(self):
        for _ in range(200):
            tm = ChatRelayMessage(
                uniq_msg_id = randrange(0,99999999),
                sender_ip = IPv4Address(randbits(32)),
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
                uniq_msg_id = randrange(0,99999999),
                sender_ip = IPv4Address(randbits(32)),
                old_message_ids = ( [randrange(0,99999999)
                        for x in range(randrange(33))] ),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_leave_relay_message(self):
        for _ in range(200):
            tm = LeaveRelayMessage(
                uniq_msg_id = randrange(0,99999999),
                sender_ip = IPv4Address(randbits(32)),
                old_message_ids = ( [randrange(0,99999999)
                        for x in range(randrange(33))] ),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_keepalive_relay_message(self):
        for _ in range(200):
            tm = KeepaliveRelayMessage(
                uniq_msg_id = randrange(0,99999999),
                sender_ip = IPv4Address(randbits(32)) )
            print(tm, unpacker(packer(tm)))
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_join_request_message(self):
        for _ in range(200):
            tm = JoinRequestMessage(
                uniq_msg_id = randrange(0,99999999),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_join_reply_message(self):
        for _ in range(200):
            tm = JoinReplyMessage(
                old_message_ids = ( [randrange(0,99999999)
                        for x in range(randrange(33))] ),
                ip_addresses = [IPv4Address(randbits(32))
                        for _ in range(randrange(2000))] )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_old_request_message(self):
        for _ in range(200):
            tm = OldRequestMessage(
                uniq_msg_id = randrange(0,99999999) )
            self.assertEqual(tm, unpacker(packer(tm)))

    def test_old_reply_message(self):
        for _ in range(200):
            tm = OldReplyMessage(
                uniq_msg_id = randrange(0,99999999),
                sender_nick = "".join(chr(randrange(1,4000))
                        for x in range(randrange(70))),
                msg_text = "".join(chr(randrange(1,4000))
                        for x in range(randrange(2000))) )
            self.assertEqual(tm, unpacker(packer(tm)))
