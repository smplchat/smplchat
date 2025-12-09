""" tui.py - a simple user interface for smplchat """
import curses
import locale
from signal import signal, SIGINT
from types import SimpleNamespace

from smplchat.message_list import MessageList

class UserInterface:
    """ class for capturing user inputs and rendering
        received messages """
    def __init__(self, messages: MessageList, username: str):

        # Add own handler for keyboard interrupt
        self.__quit_called = False
        def handler(*_):
            self.__quit_called = True

        signal(SIGINT, handler)

        # fetch the list of current messages
        self.messages = messages
        self.username = username

        # curses window objects
        self._windows = SimpleNamespace (
            stdscr=None,
            msg_win=None,
            info_win=None,
            input_win=None,
        )

        # input/layout state (cursor position, terminal size)
        self._state = SimpleNamespace (
            input_buffer="",
            cursor_pos=0,
            h=0,
            w=0,
            initialized=False,
        )

        self.start()

    def start(self) -> None:
        """ Initialize curses and create windows. """
        # try to get the locale right for UTF-8
        try:
            locale.setlocale(locale.LC_ALL, "")
        except locale.Error:
            pass

        self._windows.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self._windows.stdscr.keypad(True)
        self._windows.stdscr.nodelay(True)
        try:
            # setting cursor to visible
            curses.curs_set(1)
        except curses.error:
            pass

        self._setup_windows()
        self._state.initialized = True

    def stop(self) -> None:
        """Restore terminal state."""
        if not self._state.initialized:
            return
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        self._windows.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        self._state.initialized = False

    def _setup_windows(self) -> None:
        h, w = self._windows.stdscr.getmaxyx()
        self._state.h, self._state.w = h, w
        info_h, input_h = 3, 2
        msg_h = h - info_h - input_h
        self._windows.msg_win = self._windows.stdscr.derwin(msg_h, w, 0, 0)
        self._windows.info_win = self._windows.stdscr.derwin(info_h, w, msg_h, 0)
        self._windows.input_win = self._windows.stdscr.derwin(input_h, w, msg_h + info_h, 0)
        self._windows.msg_win.scrollok(True)

    def update(self, username):
        """ Render windows with new messages and of info, process user input.
        Returns completed input string if user has pressed enter. """
        if self.__quit_called:
            return "/quit"
        self.username = username
        if not self._state.initialized:
            raise RuntimeError("UI not started; call start() first")

        # handle window having been resized
        h, w = self._windows.stdscr.getmaxyx()
        if (h, w) != (self._state.h, self._state.w):
            self._setup_windows()

        # read available key presses and update input_buffer
        # completed = self._handle_input()
        completed = self._handle_input()
        self._render_all()
        # return message or None, if no new message from user
        return completed

    def _handle_input(self):
        completed = None
        while True:
            try:
                ch = self._windows.stdscr.get_wch()
            # no input
            except curses.error:
                break
            # is enter
            if ch == "\n":
                text = self._state.input_buffer.strip()
                self._state.input_buffer = ""
                self._state.cursor_pos = 0
                if text:
                    completed = text
                break
            # is backspace
            if ch in (curses.KEY_BACKSPACE, 127, 8, '\b', '\x7f'):
                if self._state.cursor_pos > 0:
                    self._state.input_buffer = (
                        self._state.input_buffer[: self._state.cursor_pos -1]
                        + self._state.input_buffer[self._state.cursor_pos :]
                    )
                    self._state.cursor_pos -= 1
                continue
            # is left/right arrow
            if ch == curses.KEY_LEFT:
                self._state.cursor_pos = max(0, self._state.cursor_pos - 1)
                continue
            if ch == curses.KEY_RIGHT:
                self._state.cursor_pos = min(
                    len(self._state.input_buffer),
                    self._state.cursor_pos + 1
                    )
                continue

            # some special keys, or up/down arrow
            if isinstance(ch, int):
                continue
            # is printable
            if ch.isprintable():
                self._state.input_buffer = (
                    self._state.input_buffer[: self._state.cursor_pos]
                    + ch
                    + self._state.input_buffer[self._state.cursor_pos :]
                )
                self._state.cursor_pos += 1
        return completed

    def _render_all(self) -> None:
        self._render_messages()
        self._render_info()
        self._render_input()
        # flush the virtual screen to physical screen
        try:
            curses.doupdate()
        except curses.error:
            pass

    def _render_messages(self) -> None:
        """ renders messages to message-window"""
        if not self.messages.updated:
            return
        self.messages.updated = False
        self._windows.msg_win.erase()
        lines = self.messages.get_textual_contents()
        msg_h, msg_w = self._windows.msg_win.getmaxyx()
        start = max(0, len(lines) - msg_h)
        shown = lines[start: start + msg_h]
        for i, line in enumerate(shown):
            try:
                self._windows.msg_win.addnstr(i, 0, line, msg_w - 1)
            # if something goes wrong
            except curses.error:
                pass
        self._windows.msg_win.noutrefresh()


    def _render_info(self) -> None:
        """ renders text to info-window """
        self._windows.info_win.erase()
        _, info_w = self._windows.info_win.getmaxyx()
        try:
            self._windows.info_win.hline(0, 0, "-", info_w - 1)
            self._windows.info_win.addnstr(1, 0, "/help + <enter> - show commands", info_w - 1)
            self._windows.info_win.hline(2, 0, "-", info_w - 1)
        except curses.error:
            pass
        self._windows.info_win.noutrefresh()

    def _render_input(self) -> None:
        """ renders user input """
        self._windows.input_win.erase()
        ph = f"{self.username}> "
        _, input_w = self._windows.input_win.getmaxyx()
        disp = ph + self._state.input_buffer
        try:
            self._windows.input_win.addnstr(0, 0, disp, input_w - 1)
            # move cursor
            curs_x = min(len(ph) + self._state.cursor_pos, input_w - 1)
            self._windows.input_win.move(0, curs_x)
        except curses.error:
            pass
        self._windows.input_win.noutrefresh()
