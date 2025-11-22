import time
from smplchat.listener import Listener
from smplchat.message_list import MessageList
from smplchat.dispatcher import Dispatcher

def test_dispatcher_startup():
    listener = Listener(port=62740)
    msg_list = MessageList()

    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        peers=[("127.0.0.1", 62741)],
        nick="testuser",
        self_addr=("127.0.0.1", 62740)
    )

    assert dispatcher.nick == "testuser"
    assert len(dispatcher.peers) == 1
    assert dispatcher.peers[0] == ("127.0.0.1", 62741)

    dispatcher.stop()
    listener.stop()

def test_send_chat_message_works():
    listener = Listener(port=62742)
    msg_list = MessageList()

    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        nick="bobrikov",
        self_addr=("127.0.0.1", 62742)
    )

    dispatcher.send_chat("test")

    time.sleep(0.1)

    messages = msg_list.get()
    assert len(messages) == 1
    assert messages[0].nick == "bobrikov"
    assert messages[0].message == "test"

    dispatcher.stop()
    listener.stop()

def test_add_peer():
    listener = Listener(port=62744)
    msg_list = MessageList()

    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        self_addr=("127.0.0.1", 62744),
        nick="testuser"
    )

    assert len(dispatcher.peers) == 0

    # new peer
    dispatcher.add_peer(("127.0.0.1", 62745))
    assert len(dispatcher.peers) == 1

    # same again
    dispatcher.add_peer(("127.0.0.1", 62745))
    assert len(dispatcher.peers) == 1

    # self as peer
    dispatcher.add_peer(("127.0.0.1", 62744))
    assert len(dispatcher.peers) == 1

    dispatcher.stop()
    listener.stop()
