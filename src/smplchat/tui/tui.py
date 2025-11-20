import curses
import locale

class UserInterface:
	def __init__(self, msg_list: list, username):
		self.msg_list = msg_list
		self.username = username

		# curses objects
		self.stdscr = None
		self.msg_win = None
		self.info_win = None
		self.input_win = None

		# input state
		self.input_buffer: str = ""
		self.cursor_pos: int = 0

		# layout cache - what is this?
		self._h = self._w = 0 # terminal size?
		self._initialized = False

	def start(self) -> None:
		""" Initialize curses and create windows. """
		# try to get the locale right for UTF-8
		try:
			locale.setlocale(locale.LC_ALL, "")
		except Exception:
			pass

		self.stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.stdscr.keypad(True)
		self.stdscr.nodelay(True)
		try:
			# setting cursor to visible
			curses.curs_set(1)
		except Exception:
			pass

		self._setup_windows()
		self._initialized = True

	def stop(self) -> None:
		"""Restore terminal state."""
		if not self._initialized:
			return
		try: curses.curs_set(1)
		except Exception:
			pass

		self.stdscr.keypad(False)
		curses.nocbreak()
		curses.echo()
		curses.endwin()
		self._initialized = False

	def _setup_windows(self) -> None:
		h, w = self.stdscr.getmaxyx()
		self._h, self._w = h, w
		info_h, input_h = 3, 3
		msg_h = h - info_h - input_h
		self.msg_win = self.stdscr.derwin(msg_h, w, 0, 0)
		self.info_win = self.stdscr.derwin(info_h, w, msg_h, 0)
		self.input_win = self.stdscr.derwin(input_h, w, msg_h + info_h, 0)
		self.msg_win.scrollok(True)

	def update(self):
		""" Render windows with new messages and of info, process user input.
		Returns completed input string if user has pressed enter. """

		if not self._initialized:
			raise RuntimeError("UI not started; call start() first")

		# handle window having been resized
		h, w = self.stdscr.getmaxyx()
		if (h, w) != (self._h, self._w):
			self._setup_windows()

		# read available key presses and update input_buffer
		completed = self._handle_input()
		self._render_all()
		return completed

	def _handle_input(self):
		completed = None
		while True:
			ch = self.stdscr.getch()
			# no input
			if ch == -1:
				break
			# is enter
			if ch in (curses.KEY_ENTER, 10, 13):
				text = self.input_buffer.strip()
				self.input_buffer = ""
				self.cursor_pos = 0
				if text:
					completed = text
				break
			# is backspace
			if ch in (curses.KEY_BACKSPACE, 127, 0):
				if self.cursor_pos > 0:
					self.input_buffer = (
						self.input_buffer[: self.cursor_pos -1]
						+ self.input_buffer[self.cursor_pos :]
					)
					self.cursor_pos -= 1
				continue
			# is left/right arrow
			if ch == curses.KEY_LEFT:
				self.cursor_pos = max(0, self.cursor_pos - 1)
				continue
			if ch == curses.KEY_RIGHT:
				self.cursor_pos = min(len(self.input_buffer), self.cursor_pos + 1)
				continue
			# is Ctrl-C / Ctrl-D
			if ch in (3, 4):
				raise KeyboardInterrupt
			# is printable
			if 0 <= ch < 256:
				c = chr(ch)
				if not c.isprintable():
					continue
				self.input_buffer = (
					self.input_buffer[: self.cursor_pos]
					+ c
					+ self.input_buffer[self.cursor_pos :]
				)
				self.cursor_pos += 1
		return completed

	def _render_all(self) -> None:
		self.stdscr.erase()
		self._render_messages()
		self._render_info()
		self._render_input()
		# flush the virtual screen to physical screen
		try:
			curses.doupdate()
		except Exception:
			pass

	def _render_messages(self) -> None:
		self.msg_win.erase()
		lines = [msg for msg in self.msg_list]
		msg_h, msg_w = self.msg_win.getmaxyx()
		start = max(0, len(lines) - msg_h)
		shown = lines[start: start + msg_h]
		for i, line in enumerate(shown):
			try:
				self.msg_win.addnstr(i, 0, line, msg_w - 1)
			# msg/line too long?
			except curses.error:
				pass
		self.msg_win.noutrefresh()


	def _render_info(self) -> None:
		self.info_win.erase()
		_, info_w = self.info_win.getmaxyx()
		status = f"/join to join the chat, /leave to leave the chat"
		try:
			self.info_win.addnstr(0, 0, status, info_w -1)
			self.info_win.addnstr(1, 0, "Enter=send   Ctrl-C=quit", info_w - 1)
		except curses.error:
			pass
		self.info_win.noutrefresh()

	def _render_input(self) -> None:
		self.input_win.erase()
		ph = "> "
		_, input_w = self.input_win.getmaxyx()
		disp = ph + self.input_buffer
		try:
			self.input_win.addnstr(0, 0, disp, input_w - 1)
			# move cursor
			curs_x = min(len(ph) + self.cursor_pos, input_w - 1)
			self.input_win.move(0, curs_x)
		except curses.error:
			pass
		self.input_win.noutrefresh()

if __name__ == "__main__":
	import time

	msg_list = [
		f"Aku: Hei vaan kaikille!",
		f"Iines: No tervepä terve, mitäs sinne?",
		f"Aku: Kylmiä ilmoja on pidellyt, luita kolottaa."
	]
	window = UserInterface(msg_list, "Testaaja")
	window.start()

	try:
		while True:
			completed = window.update()
			if completed:
				msg_list.append(f"{window.username}: {completed}")
			time.sleep(0.05)
	except KeyboardInterrupt:
		pass
	finally:
		window.stop()


