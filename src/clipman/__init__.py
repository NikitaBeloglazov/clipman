# -*- coding: utf-8 -*-
"""
 * Copyright (C) 2023 Nikita Beloglazov <nnikita.beloglazov@gmail.com>
 *
 * This file is part of github.com/NikitaBeloglazov/clipman.
 *
 * NikitaBeloglazov/clipman is free software; you can redistribute it and/or
 * modify it under the terms of the Mozilla Public License 2.0
 * published by the Mozilla Foundation.
 *
 * NikitaBeloglazov/clipman is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY.
 *
 * You should have received a copy of the Mozilla Public License 2.0
 * along with NikitaBeloglazov/clipman
 * If not, see https://mozilla.org/en-US/MPL/2.0.
"""
import os
import sys
import time
import shutil
import platform
import traceback
import subprocess

from . import exceptions

def debug_print(message):
	""" Prints debug messages if dataclass.debug is True :shrug: """
	if dataclass.debug is True:
		print(message)

def check_binary_installed(binary_name):
	""" Checks if binary is avalible in this OS """
	return shutil.which(binary_name) is not None

def detect_os():
	""" Detects name of OS """
	os_name = platform.system()

	if os_name == "Linux" and hasattr(sys, "getandroidapilevel"):
		# Detect Android by yourself because platform.system() detects Android as Linux
		return "Android"

	if os_name == "Darwin" and os.path.exists("/Users") and os.path.isdir("/Users"):
		# Detect macOS by specific directories in root (/)
		# by yourself because platform.system() detects macOS as Darwin, and BSD is Darwin too ( UPD: Actually, no:) )
		return "macOS"

	return os_name

def run_command(command, timeout=7, features=(), tries_maked=1):
	""" Binary file caller """
	try:
		runner = subprocess.run(command, timeout=timeout, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.TimeoutExpired as e:
		if tries_maked > 3:
			raise exceptions.EngineTimeoutExpired(f"Executing the command three times (retries), the timeout was exceeded: subprocess.TimeoutExpired: {e}")
		debug_print(f"timeout exceeded. Retry, attempt {tries_maked}")

		# Try again
		return run_command(command, timeout, features, tries_maked=tries_maked+1)

	if runner.returncode != 0:
		# - = - = - = - = - = - = - = - = - = - = - = - = - =
		# Workaround: if nothing is copied, wl-clipboard returns error code 1 with the message "Nothing is copied"

		# We catch these moments and return an empty string
		# because by default in clipman, if there is nothing copied, we need to return an empty string
		if "wl-clipboard_nothing_is_copied_is_ok" in features:
			if runner.stderr.decode('UTF-8') == "Nothing is copied\n":
				return ""
		# - = - = - = - = - = - = - = - = - = - = - = - = - =
		raise exceptions.EngineError(f"Command returned non-zero exit status: {str(runner.returncode)}.\n- = -\nSTDERR: {runner.stderr.decode('UTF-8')}")

	return runner.stdout.decode("UTF-8").removesuffix("\n") # looks like all commands returns \n in the end

def run_command_with_paste(command, text):
	""" Calls binary, gives it the text to be copied, and exits"""
	with subprocess.Popen(command, stdin=subprocess.PIPE, close_fds=True) as runner:
		runner.communicate(input=text.encode("UTF-8"))

		if runner.returncode != 0:
			raise exceptions.EngineError(f"Command returned non-zero exit status: {str(runner.returncode)}.")

		runner.terminate()
		#time.sleep(0.2)
		#runner.kill()

def check_run_command(command, engine, features=()):
	"""
	command - command to check run
	engine - string that will be returned if the check is successful
	"""
	try:
		run_command(command, features=features)
	except exceptions.EngineTimeoutExpired as e:
		raise exceptions.EngineTimeoutExpired from e
	except exceptions.ClipmanBaseException as e:
		raise exceptions.EngineError(f"\"{command}\" gives unknown error. See output for above.") from e
	return engine

class DataClass():
	""" Class for storing module data """
	def __init__(self):
		# - =
		self.klipper = None
		self.windows_native_backend = None
		# - =
		self.display_server = None
		self.current_desktop = None

		self.os_name = detect_os()
		self.engine = None
		self.init_called = False
		self.debug = False

dataclass = DataClass()

def detect_clipboard_engine():
	"""
	Detects clipboard engine based on many factors, and in many cases gives the user friendly advice.
	Returns name of detected engine
	"""
	if dataclass.os_name in ("Linux", "FreeBSD", "OpenBSD"):
		# - = - = - = - = - = - =
		# Detect graphical backend from ENV
		if "XDG_SESSION_TYPE" in os.environ:
			dataclass.display_server = os.environ["XDG_SESSION_TYPE"]
		else:
			dataclass.display_server = "< NOT SET >"
		# - = - = - = - = - = - =
		# Detect dekstop from ENV
		if "XDG_CURRENT_DESKTOP" in os.environ:
			dataclass.current_desktop = os.environ["XDG_CURRENT_DESKTOP"]
		elif "XDG_SESSION_DESKTOP" in os.environ:
			dataclass.current_desktop = os.environ["XDG_SESSION_DESKTOP"]
		elif ("KDE_SESSION_VERSION" in os.environ or
			  "KDE_FULL_SESSION" in os.environ or
			  "KDE_SESSION_UID" in os.environ or
			  "KDE_APPLICATIONS_AS_SCOPE" in os.environ):
			dataclass.current_desktop = "KDE"
		else:
			dataclass.current_desktop = "< NOT SET >"

		dataclass.current_desktop = dataclass.current_desktop.upper()
		# - = - = - = - = - = - =

		debug_print("display_server: " + dataclass.display_server)
		debug_print("current_desktop: "+ dataclass.current_desktop)

		if check_binary_installed("klipper"):
			try:
				import dbus # pylint: disable=import-outside-toplevel
				bus = dbus.SessionBus()
				dataclass.klipper = dbus.Interface(bus.get_object("org.kde.klipper", "/klipper"), "org.kde.klipper.klipper")
				dataclass.klipper.getClipboardContents(dbus_interface="org.kde.klipper.klipper")
				return 'org.kde.klipper' # If call to klipper do not raise errors, everything is OK
			except ImportError as e:
				error_message = "Please install dbus-python package.\n - Via your system package manager. Possible package names: \"python3-dbus-python\" or \"python3-dbus\"\n - Or via PIP: \"pip3 install dbus\""
				raise exceptions.AdditionalDependenciesRequired(error_message) from e
			except Exception as e: # pylint: disable=broad-except
				if dataclass.current_desktop in ("KDE", "PLASMA"):
					error_message = "An unknown error raised while initializing klipper connection via dbus.\n[!] See error above. Make issue at https://github.com/NikitaBeloglazov/clipman/issues/new?"
					raise exceptions.UnknownError(error_message) from e
				debug_print("klipper init failed:")
				debug_print(traceback.format_exc())

		if dataclass.display_server == "x11":
			if check_binary_installed("xsel"): # Preffer xsel because is it less laggy and more fresh
				return check_run_command(['xsel', '-b', '-n', '-o'], "xsel")
			if check_binary_installed("xclip"):
				return check_run_command(['xclip', '-selection', 'c', '-o'], "xclip")
			error_message = "Clipboard engines not found on your system. For Linux X11, you need to install \"xsel\" or \"xclip\" via your system package manager."
			raise exceptions.NoEnginesFoundError(error_message)

		if dataclass.display_server == "wayland":
			if check_binary_installed("wl-paste"):
				return check_run_command(['wl-paste'], "wl-clipboard", features=("wl-clipboard_nothing_is_copied_is_ok",))
			error_message = "Clipboard engines not found on your system. For Linux Wayland, you need to install \"wl-clipboard\" via your system package manager."
			raise exceptions.NoEnginesFoundError(error_message)

		if dataclass.display_server == "tty":
			error_message = "Clipboard in TTY is unsupported."
			raise exceptions.UnsupportedError(error_message)

		# If display_server is unknown
		error_message = f"The graphical backend (X11, Wayland) or running KDE was not found on your Linux OS. Check XDG_SESSION_TYPE variable in your ENV. Also, please note that TTY is unsupported.\n\nXDG_SESSION_TYPE content: {dataclass.display_server}"
		raise exceptions.NoEnginesFoundError(error_message)
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =
	if dataclass.os_name == "Android":
		if check_binary_installed("termux-clipboard-get"):
			try:
				return check_run_command(['termux-clipboard-get'], "termux-clipboard")
			except exceptions.EngineTimeoutExpired as e:
				error_message = "No usable clipboard engines found on your system. \"termux-clipboard-get\" finished with timeout, so that means Termux:API plug-in is not installed. Please install it from F-Droid and try again."
				raise exceptions.NoEnginesFoundError(error_message) from e
		else:
			error_message = "Clipboard engines not found on your system. For Android+Termux, you need to run \"pkg install termux-api\" and install \"Termux:API\" plug-in from F-Droid."
			raise exceptions.NoEnginesFoundError(error_message)
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =
	if dataclass.os_name == "Windows":
		from . import windows # pylint: disable=C0415 # import-outside-toplevel
		dataclass.windows_native_backend = windows.WindowsClipboard()
		return "windows_native_backend"
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =
	if dataclass.os_name == "macOS":
		if check_binary_installed("pbpaste"):
			return check_run_command(['pbpaste'], "pboard")
		error_message = "Clipboard engines not found on your system. For some reason, pbpaste (pboard) is not included in your macOS:((\nPlease make issue at https://github.com/NikitaBeloglazov/clipman/issues/new"
		raise exceptions.NoEnginesFoundError(error_message)
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =

	error_message = f"Clipboard engines not found on your system. Looks like \"{dataclass.os_name}\" OS is unsupported. Please make issue at https://github.com/NikitaBeloglazov/clipman/issues/new"
	raise exceptions.UnsupportedError(error_message)

def get():
	"""
	Gets & returns the clipboard content as DECODED string.
	If there is a picture or copied file (in windows), it returns an empty string
	"""
	return call("get")

def set(text): # pylint: disable=W0622 # redefined-builtin # i don't care
	"""
	Sets text to clipboard
	"""
	return call("set", text)

# Synonims
paste = get
copy = set

def call(method, text=None): # pylint: disable=R0911 # too-many-return-statements
	"""
	General method for calling engines. Very useful for maintenance

	# METHODS:
	# * set - (copy)  set to clipboard
	# * get - (paste) get text from clipboard
	"""
	if dataclass.init_called is False:
		raise exceptions.NoInitializationError
	if method == "set" and text is None:
		error_message = "Not specified text to paste!"
		raise exceptions.TextNotSpecified(error_message)

	text = str(text)

	# - = LINUX - = - = - = - = - = - = - =
	if dataclass.engine == "org.kde.klipper":
		if method == "set":
			return dataclass.klipper.setClipboardContents(text, dbus_interface="org.kde.klipper.klipper")
		if method == "get":
			return str(dataclass.klipper.getClipboardContents(dbus_interface="org.kde.klipper.klipper"))
	if dataclass.engine == "xsel":
		if method == "set":
			return run_command_with_paste(['xsel', '-b', '-i'], text)
		if method == "get":
			return run_command(['xsel', '-b', '-n', '-o'])
	if dataclass.engine == "xclip":
		if method == "set":
			return run_command_with_paste(['xclip', '-selection', 'c', '-i'], text)
		if method == "get":
			return run_command(['xclip', '-selection', 'c', '-o'])
	if dataclass.engine == "wl-clipboard":
		if method == "set":
			return run_command_with_paste(['wl-copy'], text)
		if method == "get":
			return run_command(['wl-paste'], features=("wl-clipboard_nothing_is_copied_is_ok",))
	# - = - = - = - = - = - = - = - = - = -
	# - = Android = - = - = - = - = - = - =
	if dataclass.engine == "termux-clipboard":
		if method == "set":
			return run_command_with_paste(['termux-clipboard-set'], text)
		if method == "get":
			return run_command(['termux-clipboard-get'])
	# - = - = - = - = - = - = - = - = - = -
	# - = Windows = - = - = - = - = - = - =
	if dataclass.engine == "windows_native_backend":
		if method == "set":
			return dataclass.windows_native_backend.copy(text)
		if method == "get":
			return dataclass.windows_native_backend.paste()
	# - = - = - = - = - = - = - = - = - = -
	# - = macOS = - = - = - = - = - = - =
	if dataclass.engine == "pboard":
		if method == "set":
			return run_command_with_paste(['pbcopy'], text)
		if method == "get":
			return run_command(['pbpaste'])
	# - = - = - = - = - = - = - = - = - = -
	error_message = "Specified engine not found. Have you set it manually?? ]:<"
	raise exceptions.UnknownError(error_message)

def init(debug=False):
	""" Initializes clipman, and detects copy engine for work """
	dataclass.debug = debug
	debug_print("init call start")
	dataclass.engine = detect_clipboard_engine()
	debug_print(f"detected engine: {dataclass.engine}")
	dataclass.init_called = True
