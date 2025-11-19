""" main.py - smplchat """
import socket
import time

from smplchat import listener, settings


def main():
    """ main - the entry point to the application """
    print("It's alive")

    # initialize iplist & history
    # initialize listener
    # initialize dispatcher
    # initialize message-mangler(iplist,history,listener(packet-queue),dispatcher)
    # initialize ui(history)
    # main loop:
    #	mangle loop:
    #		message-mangler-process-queue
    #	UI: do action from ui for example:
    #		join
    #		quit
    #		send message -> message-mangler

    listener.start()
    time.sleep(1)

    # Write to listener, simulates incoming messages, this will be replaced later
    address = ("", settings.PORT)
    s = socket.socket(type=socket.SOCK_DGRAM)
    time.sleep(1)

    s.sendto(b"aaaaa", address)
    s.sendto(b"aaaaa", address)
    time.sleep(1)

    messages = listener.get_messages()
    listener.stop()
    print(messages)


if __name__ == "__main__":
    main()
