import os
import sys
import shutil
import platform
import subprocess

from . import exceptions

def check_binary_installed(binary_name):
	""" Checks if binary is avalible on OS """
	return shutil.which(binary_name) is not None

def detect_os():
	""" Detects name of OS """
	os_name = platform.system()
	if platform.system() == "Linux" and hasattr(sys, "getandroidapilevel"):
		# Detect Android by yourself because platform.system() detects Android as Linux
		os_name = "Android"

	return os_name

def run_command(command):
	""" Binary file caller """
	try:
		runner = subprocess.run(command, timeout=5, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.TimeoutExpired as e:
		raise exceptions.EngineTimeoutExpired(f"The timeout for executing the command was exceeded: subprocess.TimeoutExpired: {e}")

	if runner.returncode != 0:
		raise exceptions.EngineError(f"Command returned non-zero exit status: {str(runner.returncode)}.\n- = -\nSTDERR: {runner.stdout.decode('UTF-8')}")

	return runner.stdout.decode("UTF-8").removesuffix("\n") # looks like all commands returns \n in the end

def check_run_command(command, engine):
	"""
	command - command to check run
	engine - string that will be returned if check is succeful
	"""
	try:
		run_command(command)
	except exceptions.EngineTimeoutExpired as e:
		raise exceptions.EngineTimeoutExpired from e
	except exceptions.BaseException as e:
		raise exceptions.EngineError(f"\"{command}\" gives unknown error. See output for above.") from e
	return engine

class DataClass():
	""" Just shared memory """
	def __init__(self):
		self.windows_native_backend = None

dataclass = DataClass()

def detect_copy_engine():
	"""
	Detects copy engine based on many factors, and in many cases gives the user friendly advice.
	Returns name of detected engine
	"""
	if os_name == "Linux":
		try:
			# Detect graphical backend from ENV
			graphical_backend = os.environ["XDG_SESSION_TYPE"]
		except KeyError:
			graphical_backend = "< NOT SET >"

		if graphical_backend == "x11":
			if check_binary_installed("xclip"):
				return check_run_command("xclip -selection c -o", "xclip")
			elif check_binary_installed("xsel"):
				return check_run_command("xsel", "xsel")
			else:
				raise exceptions.NoEnginesFoundError("Clipboard engines not found on your system. For Linux X11, you need to install \"xclip\" or \"xsel\" via your system package manager.")

		elif graphical_backend == "wayland":
			if check_binary_installed("wl-paste"):
				return check_run_command("wl-paste", "wl-paste")
			else:
				raise exceptions.NoEnginesFoundError("Clipboard engines not found on your system. For Linux Wayland, you need to install \"wl-clipboard\" via your system package manager.")

		elif graphical_backend == "tty":
			raise exceptions.UnsupportedError("Clipboard in TTY is unsupported.")

		# If graphical_backend is unknown
		raise exceptions.NoEnginesFoundError(f"The graphical backend (X11, Wayland) was not found on your Linux OS. Check XDG_SESSION_TYPE variable in your ENV. Also note that TTY is unsupported.\n\nXDG_SESSION_TYPE content: {graphical_backend}")
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =
	if os_name == "Android":
		if check_binary_installed("termux-clipboard-get"):
			try:
				return check_run_command("termux-clipboard-get", "termux-clipboard-get")
			except exceptions.EngineTimeoutExpired:
				raise exceptions.NoEnginesFoundError("No usable clipboard engines found on your system. \"termux-clipboard-get\" finished with timeout, so that means Termux:API plug-in is not installed. Please install it from F-Droid and try again.")
		else:
			raise exceptions.NoEnginesFoundError(f"Clipboard engines not found on your system. For Android+Termux, you need to run \"pkg install termux-api\" and install \"Termux:API\" plug-in from F-Droid.")
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =
	if os_name == "Windows":
		from . import windows
		dataclass.windows_native_backend = windows.WindowsClipboard()
		return "windows_native_backend"

	raise exceptions.NoEnginesFoundError(f"Clipboard engines not found on your system. Maybe your OS is unsupported?")

def paste():
	# - = LINUX - = - = - = - = - = - = - =
	if engine == "xclip":
		return run_command("xclip -selection c -o")
	if engine == "xsel":
		return run_command("xsel")
	if engine == "wl-paste":
		return run_command("wl-paste")
	# - = - = - = - = - = - = - = - = - = -
	# - = Android = - = - = - = - = - = - =
	if engine == "termux-clipboard-get":
		return run_command("termux-clipboard-get")
	# - = - = - = - = - = - = - = - = - = -
	# - = Android = - = - = - = - = - = - =
	if engine == "windows_native_backend":
		return dataclass.windows_native_backend.paste()
	# - = - = - = - = - = - = - = - = - = -

debug = False
os_name = detect_os()
engine = detect_copy_engine()
