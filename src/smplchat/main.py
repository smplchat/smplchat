""" main.py - smplchat """
from ipaddress import IPv4Address

from smplchat.client_list import ClientList
from smplchat.input_utils import prompt_nick
from smplchat.listener import Listener
from smplchat.message import new_message, MessageType
from smplchat.message_list import MessageList, initial_messages
from smplchat.packet_mangler import unpacker
from smplchat.sender import Sender
from smplchat.tui import UserInterface
from .utils import get_my_ip, dprint

def main():
    """ main - the entry point to the application """

    print("Welcome to smplchat!\n")

    self_ip = IPv4Address(get_my_ip())

    dprint(f"INFO: Got ip-address {self_ip}")

    # prompt nickname
    nick = prompt_nick()

    # core

    client_list = ClientList(self_ip) # Initialize ip-list

    listener = Listener()
    msg_list = MessageList()
    initial_messages(msg_list) # adds some helpful messages to the list
    sender = Sender()

    tui = UserInterface(msg_list, nick)

    msg_list.sys_message( f"*** Your IP: {self_ip}" )

    try:
        while True:

            # Process input form listener
            for rx_msg, remote_ip in listener.get_messages():
                msg = unpacker(rx_msg)
                if msg.msg_type < 128: #relay message
                    if not msg_list.is_seen(msg.uniq_msg_id):
                        msg_list.add(msg)
                        sender.send(msg, client_list.get())

                if msg.msg_type == MessageType.JOIN_REQUEST:
                    msg_list.add(msg)
                    msg_list.sys_message(
                            f"*** Join request from <{msg.sender_nick}>, "
                            f"IP: {remote_ip}")
                    # Send join reply
                    out_msg = new_message(msg_type=MessageType.JOIN_REPLY,
                            ip=self_ip, msg_list=msg_list, client_list=client_list)
                    sender.send(out_msg, [remote_ip])
                    # Send join relay message
                    out_msg = new_message(msg_type=MessageType.JOIN_RELAY,
                            nick=msg.sender_nick, text=in_txt, ip=remote_ip,
                            msg_list=msg_list )
                    sender.send(out_msg, client_list.get())
                    msg_list.sys_message(
                            f"*** Join accepted {remote_ip} ")
                    # TODO: Do the old messages
                    client_list.add(remote_ip)
                if msg.msg_type == MessageType.JOIN_REPLY:
                    msg_list.sys_message(
                        f"*** Join accepted {remote_ip} ")
                    client_list.add(remote_ip)
                    client_list.add_list(msg.ip_addresses)
            client_list.update()


            # Process input from UI
            in_txt = tui.update(nick)
            if in_txt is None:
                pass
            elif in_txt.startswith("/quit"):
                msg = new_message(msg_type=MessageType.LEAVE_RELAY, nick=nick,
                                  ip=self_ip, msg_list=msg_list)
                #    sender.send(msg)
                #    msg_list.add(msg)
                tui.stop()
                break
            elif in_txt.startswith("/nick"):
                nick = in_txt.split()[1]
            elif in_txt.startswith("/help"):
                initial_messages(msg_list)
            elif in_txt.startswith("/join"):
                msg = new_message(msg_type=MessageType.JOIN_REQUEST, nick=nick)
                try:
                    ip_pair = IPv4Address(in_txt.split()[1])
                    msg_list.sys_message(f"*** Join request sent to {ip_pair}")
                    sender.send(msg, [ip_pair])
                except:
                    msg_list.sys_message(f"*** Malformed address {in_txt.split()[1]}")
            else:  # only text to send

                msg = new_message(msg_type=MessageType.CHAT_RELAY, nick=nick,
                                  text=in_txt, ip=self_ip, msg_list=msg_list)
                msg_list.add(msg)
                sender.send(msg, client_list.get())
    finally:
        # exit cleanup
        listener.stop()
        tui.stop()

if __name__ == "__main__":
    main()
