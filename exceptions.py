
class BaseException(Exception):
	""" Used for catch all exceptions in module """
	pass

class UnsupportedError(BaseException):
	pass

class NoEnginesFoundError(BaseException):
	pass

class EngineError(BaseException):
	pass

class EngineTimeoutExpired(BaseException):
	pass