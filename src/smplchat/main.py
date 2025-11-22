""" main.py - smplchat """
from smplchat import settings
from smplchat.input_utils import parse_host_port, prompt_nick, prompt_self_addr
from smplchat.listener import Listener
from smplchat.message_list import MessageList
from smplchat.dispatcher import Dispatcher
#from smplchat.tui import run_tui

def main():
    """ Main - the entry point to the application. Chat interface TUI, but started via CLI args. """

    # prompt nickname
    nick = prompt_nick()

    # prompt address or use default
    self_addr_str = prompt_self_addr()
    self_addr = parse_host_port(self_addr_str) if self_addr_str else None

    peers = []

    listen_port = self_addr[1] if self_addr else settings.PORT

    # core
    listener = Listener(port=listen_port)
    msg_list = MessageList()
    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        peers=peers,
        nick=nick,
        self_addr=self_addr,
    )

    try:
        # curses
        #run_tui(msg_list, dispatcher, nick)
        pass # remove once dui done
    finally:
        # exit cleanup
        dispatcher.stop()
        listener.stop()

if __name__ == "__main__":
    main()
