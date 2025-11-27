""" main.py - smplchat """
import socket
from smplchat.input_utils import prompt_nick, prompt_self_addr
from smplchat.listener import Listener
from smplchat.message_list import MessageList, initial_messages
from smplchat.sender import Sender
from smplchat.tui import UserInterface
from smplchat.message import new_message, MessageType
from smplchat.client_list import ClientList
from smplchat.packet_mangler import unpacker
from .utils import get_my_ip, dprint, ip_to_int, int_to_ip

def main():
    """ main - the entry point to the application """

    print("Welcome to smplchat!\n")
    
    self_ip = ip_to_int(socket.inet_aton(get_my_ip()))

    dprint(f"INFO: Got ip-address {socket.inet_ntoa(int_to_ip(self_ip))}")

    # prompt nickname
    nick = prompt_nick()

    # core

    client_list = ClientList(self_ip) # Initialize ip-list

    listener = Listener()
    msg_list = MessageList()
    initial_messages(msg_list) # adds some helpful messages to the list
    sender = Sender()

    tui = UserInterface(msg_list, nick)

    msg_list.sys_message( f"*** Your IP: {socket.inet_ntoa(int_to_ip(self_ip))}" )

    try:
        while True:

            # Process input form listener
            for rx_msg, remote_ip in listener.get_messages():
                msg = unpacker(rx_msg)
                if msg.msg_type < 128: #relay message
                    if not msg_list.is_seen(msg.uniq_msg_id):
                        sender.send(msg, client_list.get())
                        msg_list.add(msg)
                if msg.msg_type == 128: #join request
                    msg_list.sys_message(
                            f"*** Join request from <{msg.sender_nick}>, "
                            f"IP: {socket.inet_ntoa(int_to_ip(remote_ip))}")
                    client_list.add(remote_ip)
                    # Send join reply
                    out_msg = new_message(msg_type=MessageType.JOIN_REPLY,
                            ip=self_ip, msg_list=msg_list, client_list=client_list)
                    sender.send(out_msg, [remote_ip])
                    # Send join relay message
                    out_msg = new_message(msg_type=MessageType.JOIN_RELAY,
                            nick=msg.sender_nick, text=intxt, ip=remote_ip,
                            msg_list=msg_list )
                    sender.send(out_msg, client_list.get())
                if msg.msg_type == 129: #join reply
                    msg_list.sys_message(
                            f"*** Join accepted {socket.inet_ntoa(int_to_ip(remote_ip))} ")
                    client_list.add(remote_ip)
                    # TODO: Do the old messages
                    client_list.add_list(msg.ip_addresses)
            client_list.update()
            

            # Process input from UI
            intxt = tui.update(nick)
            if intxt is None:
                pass

            elif intxt.startswith("/quit"):
                msg = new_message(msg_type=MessageType.LEAVE_RELAY, nick=nick,
                        ip=self_ip, msg_list=msg_list)
                sender.send(msg, client_list.get())
                tui.stop()
                break

            elif intxt.startswith("/nick"):
                new_nick = intxt.split()[1]
                msg = new_message(msg_type=MessageType.CHAT_RELAY, nick="system",
                        text=f"*** <{nick}> is now known as <{new_nick}>",
                        ip=self_ip, msg_list=msg_list)
                nick = new_nick
                msg_list.add(msg)
                sender.send(msg, client_list.get())

            elif intxt.startswith("/help"):
                initial_messages(msg_list)

            elif intxt.startswith("/join"):
                msg = new_message(msg_type=MessageType.JOIN_REQUEST, nick=nick)
                remote_ip = None
                try:
                    remote_ip = ip_to_int(socket.inet_aton(intxt.split()[1]))
                except OSError:
                    msg_list.sys_message(f"*** Malformed address {intxt.split()[1]}")
                if remote_ip:
                    msg_list.sys_message("*** Join request sent to "
                            f"{socket.inet_ntoa(int_to_ip(remote_ip))}")
                    sender.send(msg, [remote_ip])

            else: # only text to send
                msg = new_message(msg_type=MessageType.CHAT_RELAY, nick=nick,
                        text=intxt, ip=self_ip, msg_list=msg_list)
                msg_list.add(msg)
                sender.send(msg, client_list.get())
    finally:
        # exit cleanup
        listener.stop()
        tui.stop()

if __name__ == "__main__":
    main()
