
class ClipmanBaseException(Exception):
	""" Used for catch all exceptions in module """

class UnsupportedError(ClipmanBaseException):
	""" Called if OS or graphical backend is unsupported """

class NoEnginesFoundError(ClipmanBaseException):
	""" If usable clipboard engines not found on target OS """

class EngineError(ClipmanBaseException):
	""" If there is an error raised by clipboard engine """

class EngineTimeoutExpired(ClipmanBaseException):
	""" Called if clipboard engine calling times out. Mostly made for termux-clipboard-get """

class UnknownError(ClipmanBaseException):
	""" No comments """
