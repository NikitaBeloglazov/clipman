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
import subprocess

from . import exceptions

def check_binary_installed(binary_name):
	""" Checks if binary is avalible in this OS """
	return shutil.which(binary_name) is not None

def detect_os():
	""" Detects name of OS """
	os_name = platform.system()
	if platform.system() == "Linux" and hasattr(sys, "getandroidapilevel"):
		# Detect Android by yourself because platform.system() detects Android as Linux
		os_name = "Android"

	return os_name

def run_command(command, timeout=5):
	""" Binary file caller """
	try:
		runner = subprocess.run(command, timeout=timeout, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.TimeoutExpired as e:
		raise exceptions.EngineTimeoutExpired(f"The timeout for executing the command was exceeded: subprocess.TimeoutExpired: {e}")

	if runner.returncode != 0:
		raise exceptions.EngineError(f"Command returned non-zero exit status: {str(runner.returncode)}.\n- = -\nSTDERR: {runner.stdout.decode('UTF-8')}")

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

def check_run_command(command, engine):
	"""
	command - command to check run
	engine - string that will be returned if check is succeful
	"""
	try:
		run_command(command)
	except exceptions.EngineTimeoutExpired as e:
		raise exceptions.EngineTimeoutExpired from e
	except exceptions.ClipmanBaseException as e:
		raise exceptions.EngineError(f"\"{command}\" gives unknown error. See output for above.") from e
	return engine

class DataClass():
	""" Class for storing module data """
	def __init__(self):
		self.windows_native_backend = None
		self.os_name = detect_os()
		self.engine = None
		self.init_called = False

dataclass = DataClass()

def detect_clipboard_engine():
	"""
	Detects clipboard engine based on many factors, and in many cases gives the user friendly advice.
	Returns name of detected engine
	"""
	if dataclass.os_name == "Linux":
		try:
			# Detect graphical backend from ENV
			graphical_backend = os.environ["XDG_SESSION_TYPE"]
		except KeyError:
			graphical_backend = "< NOT SET >"

		if graphical_backend == "x11":
			if check_binary_installed("xclip"):
				return check_run_command(['xclip', '-selection', 'c', '-o'], "xclip")
			if check_binary_installed("xsel"):
				return check_run_command(['xsel'], "xsel")
			raise exceptions.NoEnginesFoundError("Clipboard engines not found on your system. For Linux X11, you need to install \"xclip\" or \"xsel\" via your system package manager.")

		if graphical_backend == "wayland":
			if check_binary_installed("wl-paste"):
				return check_run_command(['wl-paste'], "wl-clipboard")
			raise exceptions.NoEnginesFoundError("Clipboard engines not found on your system. For Linux Wayland, you need to install \"wl-clipboard\" via your system package manager.")

		if graphical_backend == "tty":
			raise exceptions.UnsupportedError("Clipboard in TTY is unsupported.")

		# If graphical_backend is unknown
		raise exceptions.NoEnginesFoundError(f"The graphical backend (X11, Wayland) was not found on your Linux OS. Check XDG_SESSION_TYPE variable in your ENV. Also note that TTY is unsupported.\n\nXDG_SESSION_TYPE content: {graphical_backend}")
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =
	if dataclass.os_name == "Android":
		if check_binary_installed("termux-clipboard-get"):
			try:
				return check_run_command(['termux-clipboard-get'], "termux-clipboard")
			except exceptions.EngineTimeoutExpired as e:
				raise exceptions.NoEnginesFoundError("No usable clipboard engines found on your system. \"termux-clipboard-get\" finished with timeout, so that means Termux:API plug-in is not installed. Please install it from F-Droid and try again.") from e
		else:
			raise exceptions.NoEnginesFoundError("Clipboard engines not found on your system. For Android+Termux, you need to run \"pkg install termux-api\" and install \"Termux:API\" plug-in from F-Droid.")
	# - = - = - = - = - = - = - = - = - = - = - = - = - = - =
	if dataclass.os_name == "Windows":
		from . import windows # pylint: disable=C0415 # import-outside-toplevel
		dataclass.windows_native_backend = windows.WindowsClipboard()
		return "windows_native_backend"

	raise exceptions.UnsupportedError(f"Clipboard engines not found on your system. Seems like \"{dataclass.os_name}\" is unsupported. Please make issue at https://github.com/NikitaBeloglazov/clipman/issues/new")

def get():
	"""
	Gets & returns clipboard content as DECODED string.
	If there is a picture or copied file(in windows), it returns empty string
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
		raise exceptions.TextNotSpecified("Not specified text to paste!")

	text = str(text)

	# - = LINUX - = - = - = - = - = - = - =
	if dataclass.engine == "xclip":
		if method == "set":
			return run_command_with_paste(['xclip', '-selection', 'c', '-i'], text)
		if method == "get":
			return run_command(['xclip', '-selection', 'c', '-o'])
	if dataclass.engine == "xsel":
		if method == "set":
			return run_command_with_paste(['xsel', '-b', '-i'], text)
		if method == "get":
			return run_command(["xsel"])
	if dataclass.engine == "wl-clipboard":
		if method == "set":
			try:
				return run_command(['wl-copy', text], timeout=3)
			except exceptions.EngineTimeoutExpired:
				return None # SEEMS like its okay, wl-copy for some reason remains in background
		if method == "get":
			return run_command(['wl-paste'])
	# - = - = - = - = - = - = - = - = - = -
	# - = Android = - = - = - = - = - = - =
	if dataclass.engine == "termux-clipboard":
		if method == "set":
			return run_command(['termux-clipboard-set', text])
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
	raise exceptions.UnknownError("Specified engine not found. Have you set it manually?? ]:<")

def init():
	""" Initializes clipman, and detects copy engine for work """
	dataclass.engine = detect_clipboard_engine()
	dataclass.init_called = True
