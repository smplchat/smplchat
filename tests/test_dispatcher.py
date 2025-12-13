import unittest
from ipaddress import IPv4Address
from unittest.mock import patch, MagicMock, call

from smplchat.udp_comms import Dispatcher
from smplchat.message import ChatRelayMessage, MessageType
from smplchat.settings import SMPLCHAT_PORT

class TestDispatcher(unittest.TestCase):

    @patch("smplchat.udp_comms.dispatcher.socket")
    @patch("smplchat.udp_comms.dispatcher.packer")
    def test_dispatcher_send(self, mock_packer, mock_socket):
        dispatcher = Dispatcher()
        mock_packer.return_value = b"BLABLA"
        sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = sock_instance
        msg = ChatRelayMessage(
            uniq_msg_id=12,
            sender_ip=666,
            old_message_ids=[],
            sender_nick="bobrikov",
            msg_text="hi",
        )

        ips = [
            IPv4Address("127.0.0.1"),
            IPv4Address("8.8.8.8"),
        ]

        dispatcher.send(msg, ips)

        self.assertEqual(mock_packer.call_count, 2)
        mock_packer.assert_has_calls([call(msg), call(msg)])
        mock_socket.assert_called_once()
        expected_calls = [
            (b"BLABLA", ("127.0.0.1", SMPLCHAT_PORT)),
            (b"BLABLA", ("8.8.8.8", SMPLCHAT_PORT)),
        ]
        actual_calls = [c.args for c in sock_instance.sendto.call_args_list]
        self.assertEqual(expected_calls, actual_calls)

    @patch("smplchat.udp_comms.dispatcher.socket")
    @patch("smplchat.udp_comms.dispatcher.packer")
    def test_dispatcher_no_send_empty_ip_list(self, mock_packer, mock_socket):
        dispatcher = Dispatcher()

        mock_packer.return_value = b"BLABLA"

        msg = ChatRelayMessage(
            uniq_msg_id=12,
            sender_ip=666,
            old_message_ids=[],
            sender_nick="aa",
            msg_text="aa",
        )

        dispatcher.send(msg, [])

        sock_instance = mock_socket.return_value.__enter__.return_value

        mock_packer.assert_not_called()
        sock_instance.sendto.assert_not_called()
