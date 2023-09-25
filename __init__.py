import os
import sys
import shutil
import platform
import subprocess

from . import exceptions

def check_binary_installed(binary_name):
	return shutil.which(binary_name) is not None

def detect_os():
	os_name = platform.system()
	if platform.system() == "Linux" and hasattr(sys, "getandroidapilevel"):
		# Detect Android by yourself because platform.system() detects Android as Linux
		os_name = "Android"

	return os_name

def run_command(command):
	try:
		runner = subprocess.run(command, timeout=5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.TimeoutExpired as e:
		raise exceptions.EngineError(f"The timeout for executing the command was exceeded: subprocess.TimeoutExpired: {e}")

	if runner.returncode != 0:
		raise exceptions.EngineError(f"Command returned non-zero exit status: {str(runner.returncode)}.")

	return runner.stdout.decode("UTF-8").removesuffix("\n") # looks like all commands returns \n in the end

def detect_copy_engine():
	if os_name == "Linux":
		try:
			graphical_backend = os.environ["XDG_SESSION_TYPE"]
		except KeyError:
			graphical_backend = "< NOT SET >"
		
		if graphical_backend == "x11":
			if check_binary_installed("xclip"):
				check_run = subprocess.run("xclip -rmlastnl -selection c -o", shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				if check_run.returncode == 0:
					return "xclip"
				else:
					raise exceptions.EngineError(f"Xclip gives unknown error:\n\n{check_run.stderr.decode('utf-8')}")
			elif check_binary_installed("xsel"):
				check_run = subprocess.run("xsel", shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				if check_run.returncode == 0:
					return "xsel"
				else:
					raise exceptions.EngineError(f"Xsel gives unknown error:\n\n{check_run.stderr.decode('utf-8')}")
			else:
				raise exceptions.NoEnginesFoundError("Clipboard engines not found on your system. For Linux X11, you need to install \"xclip\" or \"xsel\" via your system package manager.")
		
		elif graphical_backend == "wayland":
			if check_binary_installed("wl-paste"):
				check_run = subprocess.run("wl-paste", shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				if check_run.returncode == 0:
					return "wl-paste"
				else:
					raise exceptions.EngineError(f"wl-paste gives unknown error:\n\n{check_run.stderr.decode('utf-8')}")
			else:
				raise exceptions.NoEnginesFoundError("Clipboard engines not found on your system. For Linux Wayland, you need to install \"wl-clipboard\" via your system package manager.")

		elif graphical_backend == "tty":
			raise exceptions.UnsupportedError("Clipboard in TTY is unsupported.")

		# If there was a command execution error, xclip, xsel and wl-clipboard is not installed
		raise exceptions.NoEnginesFoundError(f"The graphical backend (X11, Wayland) was not found on your Linux OS. Check XDG_SESSION_TYPE variable in your ENV. Also note that TTY is unsupported\n\nXDG_SESSION_TYPE content: {graphical_backend}")

	elif os_name == "Android":
		if check_binary_installed("termux-clipboard-get"):
			try:
				check_run = subprocess.run("termux-clipboard-get", timeout=5, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				if check_run.returncode == 0:
					return "termux-clipboard-get"
				else:
					raise exceptions.EngineError(f"termux-clipboard-get gives unknown error:\n\n{check_run.stderr.decode('utf-8')}")
			except subprocess.TimeoutExpired:
				raise exceptions.NoEnginesFoundError("Usable clipboard engines not found on your system. \"termux-clipboard-get\" finished with timeout, so that means Termux:API plug-in is not installed. Please install it from F-Droid and try again.")
		else:
			raise exceptions.NoEnginesFoundError(f"Clipboard engines not found on your system. For Android+Termux, you need to run \"pkg install termux-api\" and install \"Termux:API\" plug-in from F-Droid.")

	raise exceptions.NoEnginesFoundError(f"Clipboard engines not found on your system. Maybe your OS is unsupported?")

def paste():
	print("used engine: " + engine)
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


os_name = detect_os()
engine = detect_copy_engine()
