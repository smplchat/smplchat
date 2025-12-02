import pytest
from ipaddress import IPv4Address
from smplchat.message import message_gen
from smplchat.message import MessageType, KeepaliveRelayMessage

def test_keepalive(monkeypatch):
    monkeypatch.setattr(message_gen, "generate_uid", lambda: 666)
    msg = message_gen.new_message(MessageType.KEEPALIVE_RELAY, ip=IPv4Address("11.1.1.1"))

    assert isinstance(msg, KeepaliveRelayMessage)
    assert msg.msg_type == MessageType.KEEPALIVE_RELAY
    assert msg.msg_type == 3
    assert msg.uniq_msg_id == 666
    assert msg.sender_ip == IPv4Address("11.1.1.1")

def test_keepalive_missing_ip():
    with pytest.raises(KeyError):
        message_gen.new_message(MessageType.KEEPALIVE_RELAY)
