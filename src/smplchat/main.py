""" main.py - smplchat """
from smplchat import settings
from smplchat.argparsing import parse_args, parse_host_port, parse_partners
from smplchat.listener import Listener
from smplchat.message_list import MessageList
from smplchat.dispatcher import Dispatcher
#from smplchat.tui import run_tui

def main():
    """ Main - the entry point to the application. Chat interface TUI, but started via CLI args. """
    args = parse_args()

    self_addr = parse_host_port(args.self_addr) if args.self_addr else None
    peers = parse_partners(args.partners)

    listen_port = self_addr[1] if self_addr else settings.PORT

    # core
    listener = Listener(port=listen_port)
    msg_list = MessageList()
    dispatcher = Dispatcher(
        listener=listener,
        message_list=msg_list,
        peers=peers,
        nick=args.nick,
        self_addr=self_addr,
    )

    # backwards compatibility with full CLI start using --partners
    if peers:
        dispatcher.send_join()

    try:
        # curses
        #run_tui(msg_list, dispatcher, args.nick)
        pass
    finally:
        # exit cleanup
        dispatcher.stop()
        listener.stop()

if __name__ == "__main__":
    main()
