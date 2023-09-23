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

def paste():
	print("used engine: " + engine)
	if engine == "xclip":
		return run_command("xclip -selection c -o")
	elif engine == "xsel":
		return run_command("xsel")
	elif engine == "wl-paste":
		return run_command("wl-paste")

os_name = detect_os()
engine = detect_copy_engine()
