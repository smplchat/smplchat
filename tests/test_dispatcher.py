import time
from smplchat.listener import Listener
from smplchat.message_list import MessageList
from smplchat.dispatcher import Dispatcher
from smplchat.client_list import ClientList

def test_dispatcher_startup():
    listener = Listener("")
    msg_list = MessageList()
    ip_list = ClientList(("127.0.0.1", 62740))

    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        client_list=ip_list,
        nick="testuser",
        self_addr=("127.0.0.1", 62740)
    )

    assert dispatcher.nick == "testuser"
    assert dispatcher.self_addr == ("127.0.0.1", 62740)

    assert dispatcher._thread.is_alive()
    
    # check they're using the same socket
    assert dispatcher.sock is listener.sock
    
    # check the connected boolean at startup, this could change with different startup style
    assert dispatcher.connected == True

    dispatcher.stop()
    listener.stop()

    # check shutdown succeeded
    assert not dispatcher._thread.is_alive()

def test_send_chat_message_works():
    listener = Listener("")
    msg_list = MessageList()
    ip_list = ClientList(("127.0.0.1", 62742))

    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        client_list=ip_list,
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

def test_add_and_remove_peer():
    """This was a test for dispatcher's peerlist. Now this remnant ended up testing clientlist through dispatcher."""
    listener = Listener("")
    msg_list = MessageList()
    ip_list = ClientList(("127.0.0.1", 62744))

    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        client_list=ip_list,
        self_addr=("127.0.0.1", 62744),
        nick="testuser"
    )

    assert len(dispatcher.client_list.get(n=100)) == 0

    # new peer
    dispatcher.client_list.add(("127.0.0.1", 62745))
    assert len(dispatcher.client_list.get(n=100)) == 1

    # same again
    dispatcher.client_list.add(("127.0.0.1", 62745))
    assert len(dispatcher.client_list.get(n=100)) == 1

    # self as peer
    dispatcher.client_list.add(("127.0.0.1", 62744))
    assert len(dispatcher.client_list.get(n=100)) == 1

    # another actual new peer
    dispatcher.client_list.add(("127.0.0.1", 62746))
    assert len(dispatcher.client_list.get(n=100)) == 2

    # remove peer
    dispatcher.client_list.remove(("127.0.0.1", 62745))
    assert len(dispatcher.client_list.get(n=100)) == 1

    # clear
    dispatcher.client_list.clear()
    assert len(dispatcher.client_list.get(n=100)) == 0

    dispatcher.stop()
    listener.stop()
