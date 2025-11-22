""" main.py - smplchat """
from smplchat.input_utils import prompt_nick, prompt_self_addr
from smplchat.listener import Listener
from smplchat.message_list import MessageList, initial_messages
from smplchat.dispatcher import Dispatcher
from smplchat.tui import UserInterface
from smplchat.message import new_message
from smplchat.client_list import ClientList

def main():
    """ main - the entry point to the application """

    print("Welcome to smplchat!")

    # prompt nickname
    nick = prompt_nick()

    # prompt address or use default
    self_addr = prompt_self_addr()

    # core

    ip_list = ClientList(self_addr) # Initialize ip-list

    listener = Listener(port=self_addr[1])
    msg_list = MessageList()
    initial_messages(msg_list) # adds some helpful messages to the list
    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        nick=nick,
        self_addr=self_addr
    )

    tui = UserInterface(msg_list, nick)

    while True:
        #for rx_msg in listener.update():
        #    msg = unpacker(rx_msg)
        #    if msg.type < 128: #relay message
        #	if msg_list.is_seen:
        #          dispatcher.send(message)
        ip_list.update()
        intxt = tui.update(nick)
        if intxt is None:
            continue
        if intxt.startswith("/nick"):
            nick = intxt.split()[1]
            continue
        if intxt.startswith("/quit"):
        #    msg = LeaveRelayMessage(...)
        #    dispatcher.send(msg)
        #    msg_list.add(msg)
            tui.stop()
            break

        msg = new_message(nick, intxt, self_addr, msg_list)
        msg_list.add(msg)
        #dispatcher.send(msg)


    #try:
        # curses
        #run_tui(msg_list, dispatcher, nick)
        #pass # remove once tui done
    #finally:
        # exit cleanup
    dispatcher.stop()
    listener.stop()
    tui.stop()

if __name__ == "__main__":
    main()
