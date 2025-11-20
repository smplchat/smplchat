""" list - Provides message list and methods to manipulate it """
from smplchat.packet_mangler import Message

class MessageList:
	""" MessageList - The actual class """
	def __init__(self):
		self.__messages = []

	def __update(self):
		""" __update - internal command that for example cut too long list"""

	def add(self, msg: Message):
		""" add - Adds message and its history to the list """

	def find(self, uid):
		""" find - finds if there is already message of uid """

	def get(self):
		""" get - Gets current list """
		self.__update()
		return self.__messages
