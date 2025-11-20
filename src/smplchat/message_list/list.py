""" list - Provides message list and methods to manipulate it """
from dataclasses import dataclass
from smplchat.packet_mangler import (
	Message,
	ChatRelayMessage,
	JoinRelayMessage,
	LeaveRelayMessage)

@dataclass
class MessageEntry:
	""" Entry in the message list
	
		Details:
		uid - unique ID of message
		seen - counter how many times message is added
		time - senders local time
		nick - the nick of sender
		message - message content
	"""
	uid: int
	seen: int
	time: int
	nick: str
	message: str

class MessageList:
	""" MessageList - The class for the list. """
	def __init__(self):
		self.__messages = []
		self.updated = False

	def __update(self):
		""" __update - internal command that for example cut too long list"""

	def __add_unseen_history(self, history: list[int]):
		""" __add_unseen_history - adds unseen messages to
			the message list in corrent order. """

	def add(self, msg: Message):
		""" add - Adds message and its history to the list """
		if isinstance(msg, ChatRelayMessage):
			pos = self.find(msg.uniq_msg_id)
			if pos is not None:
				old_msg = self.__messages[pos]
				self.__messages[pos] = MessageEntry (
					uid = old_msg.uid,
					seen = old_msg.seen + 1,
					time = msg.sender_local_time,
					nick = msg.sender_nick,
					message = msg.msg_text	)
				self.updated = True
				return True
			self.__messages.append(MessageEntry (
				uid = msg.uniq_msg_id,
				seen = 1,
				time = msg.sender_local_time,
				nick = msg.sender_nick,
				message = msg.msg_text	) )
			return True
			
		if isinstance(msg, JoinRelayMessage):
			pass

		if isinstance(msg, LeaveRelayMessage):
			pass
		return False

	def find(self, uid: int):
		""" find - finds if there is already message of uid
			returns position in the list or None
		"""
		return None

	def get(self):
		""" get - Gets current list """
		self.__update()
		return self.__messages
