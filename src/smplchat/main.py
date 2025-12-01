""" main.py - smplchat """
from ipaddress import IPv4Address, AddressValueError
from smplchat.listener import Listener
from smplchat.message_list import MessageList, initial_messages
from smplchat.dispatcher import Dispatcher
from smplchat.tui import UserInterface
from smplchat.message import new_message, MessageType
from smplchat.client_list import ClientList
from smplchat.packet_mangler import unpacker
from smplchat.utils import get_my_ip, dprint


def main():
    """ main - the entry point to the application """

    print("Welcome to smplchat!\n")

    self_ip = get_my_ip()

    dprint(f"INFO: Got ip-address {str(self_ip)}")

    # prompt nickname
    nick = input("Enter nickname for chat: ").strip() or "anon"

    # core
    client_list = ClientList(self_ip)  # Initialize ip-list
    listener = Listener()
    msg_list = MessageList()
    initial_messages(msg_list)  # adds some helpful messages to the list
    dispatcher = Dispatcher()
    tui = UserInterface(msg_list, nick)

    msg_list.sys_message(f"*** Your IP: {str(self_ip)}")

    try:
        while True:

            # Process input form listener
            for rx_msg, remote_ip in listener.get_messages():
                msg = unpacker(rx_msg)
                if msg.msg_type < 128:  # relay message
                    if not msg_list.is_seen(msg.uniq_msg_id):
                        dispatcher.send(msg, client_list.get())
                        msg_list.add(msg)
                if msg.msg_type == 128:  # join request
                    msg_list.sys_message(
                        f"*** Join request from <{msg.sender_nick}>, "
                        f"IP: {str(remote_ip)}")
                    client_list.add(remote_ip)
                    # Send join reply
                    out_msg = new_message(msg_type=MessageType.JOIN_REPLY,
                                          ip=self_ip, msg_list=msg_list, client_list=client_list)
                    dispatcher.send(out_msg, [remote_ip])
                    # Send join relay message
                    out_msg = new_message(msg_type=MessageType.JOIN_RELAY,
                                          nick=msg.sender_nick, ip=remote_ip,
                                          msg_list=msg_list)
                    dispatcher.send(out_msg, client_list.get())
                if msg.msg_type == 129:  # join reply
                    msg_list.sys_message(
                        f"*** Join accepted {str(remote_ip)} ")
                    client_list.add(remote_ip)
                    # TODO: Do the old messages # pylint: disable=["fixme"]
                    client_list.add_list(msg.ip_addresses)
                if msg.msg_type == MessageType.OLD_REPLY:
                    msg_list.add(msg)
                if msg.msg_type == MessageType.OLD_REQUEST:
                    found = msg_list.get_by_uid(msg.uniq_msg_id)
                    if found is not None:
                        msg = new_message(MessageType.OLD_REPLY, old_type=found.mtype, uid=msg.uniq_msg_id,
                                          nick=found.nick, text=found.message)
                        dispatcher.send(msg, [remote_ip])
            client_list.update()

            # Process input from UI
            intxt = tui.update(nick)
            if intxt is None:
                pass

            elif intxt.startswith("/quit"):
                msg = new_message(msg_type=MessageType.LEAVE_RELAY, nick=nick,
                                  ip=self_ip, msg_list=msg_list)
                dispatcher.send(msg, client_list.get())
                tui.stop()
                break

            elif intxt.startswith("/nick"):
                new_nick = intxt.split()[1]
                msg = new_message(msg_type=MessageType.CHAT_RELAY, nick="system",
                                  text=f"*** <{nick}> is now known as <{new_nick}>",
                                  ip=self_ip, msg_list=msg_list)
                nick = new_nick
                msg_list.add(msg)
                dispatcher.send(msg, client_list.get())

            elif intxt.startswith("/help"):
                initial_messages(msg_list)

            elif intxt.startswith("/join"):
                msg = new_message(msg_type=MessageType.JOIN_REQUEST, nick=nick)
                remote_ip = None
                try:
                    remote_ip = IPv4Address(intxt.split()[1])
                except IndexError:
                    msg_list.sys_message(f"*** Join needs address")
                except AddressValueError:
                    msg_list.sys_message(f"*** Malformed address {intxt.split()[1]}")
                if remote_ip:
                    msg_list.sys_message(f"*** Join request sent to {str(remote_ip)}")
                    dispatcher.send(msg, [remote_ip])

            else:  # only text to send
                msg = new_message(msg_type=MessageType.CHAT_RELAY, nick=nick,
                                  text=intxt, ip=self_ip, msg_list=msg_list)
                msg_list.add(msg)
                dispatcher.send(msg, client_list.get())

            # Fetch missing messages from peers
            waiting_message = msg_list.get_waiting_message()
            if waiting_message is not None:
                msg = new_message(MessageType.OLD_REQUEST, uid=waiting_message)
                dispatcher.send(msg,client_list.get(1))
    finally:
        # exit cleanup
        listener.stop()
        tui.stop()

if __name__ == "__main__":
    main()
