class _Getch:
	"""
	Gets a single character from standard input.  Does not echo to the screen.
	"""
	def __init__(self):
		try:
			self.impl = _GetchWindows()
			self.platform = 'windows'
		except ImportError:
			try:
				self.impl = _GetchMacCarbon()
				self.platform = 'mac'
			except(AttributeError, ImportError):
				self.impl = _GetchUnix()
				self.platform = 'unix'

	def __call__(self):
		return self.impl()


class _GetchUnix:

	def __init__(self):
		import tty
		import sys
		import termios  # import termios now or else you'll get the Unix version on the Mac
		
	def __call__(self):
		import sys
		import tty
		import termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch


class _GetchWindows:
	
	def __init__(self):
		import msvcrt

	def __call__(self):
		import msvcrt
		akey = msvcrt.getch()
		if akey == '\xe0' or akey == '\000':
			raise KeyboardInterrupt('break for ctrl-tab and others')
		return akey


class _GetchMacCarbon:
	"""
	A function which returns the current ASCII key that is down;
	if no ASCII key is down, the null string is returned.
	"""
	
	def __init__(self):
		import Carbon
		test = Carbon.Evt  # see if it has this (in Unix, it doesn't)

	def __call__(self):
		import Carbon
		if Carbon.Evt.EventAvail(0x0008)[0] == 0:  # 0x0008 is the keyDownMask
			return ''
		else:
			(what, msg, when, where, mod) = Carbon.Evt.GetNextEvent(0x0008)[1]
			return chr(msg & 0x000000FF)


def flushKeybuffer(keypress):
	import sys
	sys.stdout.flush()
	
	if keypress.platform == 'windows':
		import msvcrt
		# Try to flush the buffer
		while msvcrt.kbhit():
			msvcrt.getch()
	
	else:
		from termios import tcflush, TCIOFLUSH
		tcflush(sys.stdin, TCIOFLUSH)
	
	return
