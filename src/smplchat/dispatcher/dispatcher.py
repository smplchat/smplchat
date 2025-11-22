"""dispatcher - gossip message dispatcher """
# many attributes in the system as a whole, maybe look into this later
# pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-positional-arguments,broad-exception-caught

import socket
import struct
import time
import random
import threading

from smplchat.settings import dprint
from smplchat.packet_mangler import (
    MessageType,
    ChatRelayMessage,
    JoinRelayMessage,
    LeaveRelayMessage,
    packer,
    unpacker,
)

def _new_uid():
    """Randomizer and time used for ID."""
    return int(time.time() * 1000) ^ random.getrandbits(32)

def _ip_to_int(ip_str):
    """Convert string to int for packet mangler."""
    try:
        return struct.unpack("!L", socket.inet_aton(ip_str))[0]
    except OSError:
        return 0

class Dispatcher:
    """Dispatcher for handling packets that the listener has put in a queue."""
    def __init__(
        self,
        listener,
        message_list,
        peers=None,
        nick=None,
        self_addr=None,
        poll_interval=0.05,
    ):
        self.listener = listener
        self.msg_list = message_list
        self.nick = nick
        self.poll_interval = poll_interval
        self.connected = True

        if self_addr is None or nick is None:
            raise ValueError("self_addr and nick required")

        # own address
        host, port = self_addr
        self.self_addr = (host, int(port))

        # convert own address IP into int
        self.self_ip_int = _ip_to_int(self.self_addr[0])

        # peers
        self.peers: list[tuple[str, int]] = []
        for p in peers or []:
            self.add_peer(p)

        # socket from listener for peer discovery (couldn't manage it with separate)
        self.sock = self.listener.sock

        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def add_peer(self, addr):
        """Add peer, ignoring duplicates and self."""
        host, port = addr
        peer = (host, int(port))

        if peer == self.self_addr:
            return

        if peer not in self.peers:
            self.peers.append(peer)
            dprint("dispatcher: added peer", peer)

    def remove_peer(self, addr):
        """Remove peer."""
        host, port = addr
        peer = (host, int(port))
        if peer in self.peers:
            self.peers.remove(peer)
            dprint("dispatcher: removed peer", peer)

    def _make_and_send(self, msg_cls, msg_type, **extra):
        """Common code for messages."""
        old_ids = []
        if hasattr(self.msg_list, "latest_ids"):
            try:
                old_ids = self.msg_list.latest_ids(32)
            except Exception:
                old_ids = []

        if msg_type == MessageType.JOIN_RELAY:
            self.connected = True

        msg = msg_cls(
            msg_type=msg_type,
            uniq_msg_id=_new_uid(),
            sender_ip=self.self_ip_int,
            sender_local_time=int(time.time()),
            old_message_ids=old_ids,
            sender_nick=self.nick,
            **extra,
        )
        self._store_and_gossip(msg)

    def send_chat(self, text):
        """Basic chat message."""
        self._make_and_send(
            ChatRelayMessage,
            MessageType.CHAT_RELAY,
            msg_text=text,
        )

    def send_join(self):
        """Join message."""
        self._make_and_send(
            JoinRelayMessage,
            MessageType.JOIN_RELAY,
        )

    def send_leave(self):
        """Leave message."""
        self._make_and_send(
            LeaveRelayMessage,
            MessageType.LEAVE_RELAY,
        )

    def leave_chat(self):
        """Leave chat but not app."""
        if not self.connected:
            return

        # leave notice
        self.send_leave()

        # no gossiping
        self.connected = False
        self.peers.clear()

    def _loop(self):
        """Actual loop for incoming packets."""
        while not self._stop:
            packets = self.listener.get_messages()
            if not packets:
                time.sleep(self.poll_interval)
                continue

            for data, addr in packets:
                self._handle_packet(data, addr)

    def _handle_packet(self, data: bytes, addr: tuple[str, int]):
        """Unpacks one packet into a message. Also adds sender as peer."""
        try:
            msg = unpacker(data)
        except Exception as e:
            dprint("dispatcher: unpack failed:", e)
            return

        if not self.connected:
            return

        # for now leave adds peer, but it shouldn't once the leave message gets further refined
        if isinstance(msg, (ChatRelayMessage, JoinRelayMessage, LeaveRelayMessage)):
            self.add_peer(addr)
            self._handle_relay(msg)

    def _handle_relay(self, msg):
        """Adds incoming message to list. If it's new it's sent on."""
        try:
            is_new = self.msg_list.add(msg) # new IDs = True, duplicates = False
        except Exception as e:
            dprint("dispatcher: msg_list.add failed (remote):", e)
            return

        if is_new:
            self._broadcast(msg)

    def _store_and_gossip(self, msg):
        """Same as above but for outgoing."""
        self.msg_list.add(msg)
        self._broadcast(msg)

    def _broadcast(self, msg):
        """Send message to others via UDP."""
        if not self.connected:
            return

        data = packer(msg)
        if not data:
            return
        for addr in list(self.peers):
            try:
                self.sock.sendto(data, addr)
            except OSError as e:
                dprint("dispatcher: sendto failed:", addr, e)

    def stop(self):
        """Stops the thread."""
        self._stop = True
        try:
            self._thread.join(timeout=1)
        except RuntimeError:
            pass
