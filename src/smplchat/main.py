""" main.py - smplchat """
from smplchat.input_utils import prompt_nick, prompt_self_addr
from smplchat.listener import Listener
from smplchat.message_list import MessageList
from smplchat.dispatcher import Dispatcher
#from smplchat.tui import run_tui

def main():
    """ main - the entry point to the application """

    print("Welcome to smplchat!")

    # prompt nickname
    nick = prompt_nick()

    # prompt address or use default
    self_addr = prompt_self_addr()

    # core
    listener = Listener(port=self_addr[1])
    msg_list = MessageList()
    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        nick=nick,
        self_addr=self_addr
    )

    try:
        # curses
        #run_tui(msg_list, dispatcher, nick)
        pass # remove once tui done
    finally:
        # exit cleanup
        dispatcher.stop()
        listener.stop()

if __name__ == "__main__":
    main()
