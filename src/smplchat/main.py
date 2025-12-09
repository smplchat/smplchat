""" main.py - smplchat """
from ipaddress import IPv4Address, AddressValueError
from time import time
from smplchat.listener import Listener
from smplchat.message_list import MessageList, initial_messages
from smplchat.dispatcher import Dispatcher
from smplchat.tui import UserInterface
from smplchat.message import (
        MessageType,
        KeepaliveRelayMessage,
        JoinRequestMessage,
        JoinReplyMessage,
        OldRequestMessage,
        OldReplyMessage,
        is_relay_message,
        new_message)
from smplchat.client_list import ClientList, KeepaliveList
from smplchat.packet_mangler import unpacker
from smplchat.utils import get_my_ip, dprint
from smplchat.settings import KEEPALIVE_INTERVAL, SMPLCHAT_NICK

def main():
    """ main - the entry point to the application """

    print("Welcome to smplchat!\n")

    self_ip = get_my_ip()

    dprint(f"INFO: Got ip-address {str(self_ip)}")

    # prompt nickname
    if SMPLCHAT_NICK:
        nick = SMPLCHAT_NICK
    else:
        try:
            nick = input("Enter nickname for chat: ").strip() or "anon"
        except KeyboardInterrupt:
            print("\nExited smplchat")
            return

    # core initializations
    client_list = ClientList(self_ip) # Initialize ip-list
    listener = Listener()
    msg_list = MessageList()
    keepalive_list = KeepaliveList()
    initial_messages(msg_list) # adds some helpful messages to the list
    dispatcher = Dispatcher()
    tui = UserInterface(msg_list, nick)
    last_keepalive = time()

    msg_list.sys_message( f"*** Your IP: {str(self_ip)}" )

    # main event loop: processes messaging and tui input/output
    try:
        while True:

            # Process input form listener
            for rx_msg, remote_ip in listener.get_messages():
                msg = unpacker(rx_msg)
                if isinstance(msg, KeepaliveRelayMessage):
                    client_list.add(msg.sender_ip) # keepalive sender is alive
                    if keepalive_list.seen_count(msg.uniq_msg_id) < 2:
                        dispatcher.send(msg,client_list.get(exclude=remote_ip))
                    keepalive_list.add(msg.uniq_msg_id)

                elif is_relay_message(msg):
                    client_list.add(remote_ip) # relayer is alive
                    seen = msg_list.is_seen(msg.uniq_msg_id)
                    if not seen or seen < 2: # resend first 2 times
                        # orginal sender is alive so add to the list
                        client_list.add(msg.sender_ip)
                        # relay messages to other peers
                        dispatcher.send(
                                msg, client_list.get(exclude=remote_ip))
                        msg_list.add(msg) # add or update seend count

                elif isinstance(msg, JoinRequestMessage):
                    msg_list.sys_message(
                            f"*** Join request from <{msg.sender_nick}>, "
                            f"IP: {str(remote_ip)}")
                    client_list.add(remote_ip)
                    # Send join reply
                    out_msg = new_message(msg_type=MessageType.JOIN_REPLY,
                            ip=self_ip, msg_list=msg_list,
                            client_list=client_list)
                    dispatcher.send(out_msg, [remote_ip])
                    # Send join relay message
                    out_msg = new_message(msg_type=MessageType.JOIN_RELAY,
                            nick=msg.sender_nick, ip=remote_ip,
                            msg_list=msg_list )
                    msg_list.add(out_msg)
                    dispatcher.send(out_msg, client_list.get())

                elif isinstance(msg, JoinReplyMessage):
                    msg_list.sys_message(
                            f"*** Join accepted {str(remote_ip)} ")
                    client_list.add(remote_ip)
                    client_list.add_list(msg.ip_addresses)

                elif isinstance(msg, OldReplyMessage):
                    msg_list.add(msg)

                elif isinstance(msg, OldRequestMessage):
                    found = msg_list.get_by_uid(msg.uniq_msg_id)
                    if found is not None:
                        msg = new_message(MessageType.OLD_REPLY,
                                old_type=MessageType.CHAT_RELAY,
                                uid=msg.uniq_msg_id,
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
                msg = new_message(
                        msg_type=MessageType.CHAT_RELAY, nick="system",
                        text=f"*** <{nick}> is now known as <{new_nick}>",
                        ip=self_ip, msg_list=msg_list )
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
                    msg_list.sys_message("*** Join needs address")
                except AddressValueError:
                    msg_list.sys_message(
                            f"*** Malformed address {intxt.split()[1]}")
                if remote_ip:
                    msg_list.sys_message(
                            f"*** Join request sent to {str(remote_ip)}")
                    dispatcher.send(msg, [remote_ip])

            else: # only text to send
                msg = new_message(msg_type=MessageType.CHAT_RELAY, nick=nick,
                        text=intxt, ip=self_ip, msg_list=msg_list)
                msg_list.add(msg)
                dispatcher.send(msg, client_list.get())

            # Fetch missing messages from peers
            waiting_message = msg_list.get_waiting_message()
            if waiting_message is not None:
                msg = new_message(MessageType.OLD_REQUEST, uid=waiting_message)
                dispatcher.send(msg,client_list.get(1))

            # keepalive
            if time() - last_keepalive >= KEEPALIVE_INTERVAL:
                peers = client_list.get()
                if peers:
                    ka_msg = new_message(
                        msg_type=MessageType.KEEPALIVE_RELAY,
                        ip=self_ip,
                    )
                    dispatcher.send(ka_msg, peers)
                last_keepalive = time()

            # maintenance
            keepalive_list.cleanup()
            client_list.update()
    finally:
        # exit cleanup
        listener.stop()
        tui.stop()
        print("Exited smplchat")

if __name__ == "__main__":
    main()
