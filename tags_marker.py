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

- = - =
 * Module Decsription:
 In short, all it does is find the latest release number using git,
 and replace the special placeholders (!!{PLACEHOLDER}!!)
 with the latest release version number that it finds.

 This module is mostly designed for automatic assembly.

 [!!] Works only if the folder has the git system initialized.
 (In simple, `git clone` and `.git` folder is required)

 # TODO?: Change this file name
"""

# - DEBUG -
#import os
#os.system("tree -a")
#os.system("git fetch --tags")
#print(subprocess.check_output("git tag -n9", shell=True, encoding="UTF-8"))

import subprocess

# - Get current tag
tag = subprocess.check_output("git describe --tags", shell=True, encoding="UTF-8")
print("[TAG MARKER] git response: " + tag)

# - Clear tag from junk, you need to get numbers with dots only
tag = tag.replace("\n", "").replace("v", "")
if tag.find("-") > 1:
	tag = tag[0:tag.find("-")]
print("[TAG MARKER] FOUND TAG: " + tag)

# - Mark pyproject.toml
print("[TAG MARKER] MARKING VERSION IN pyproject.toml")
with open('pyproject.toml', 'r+', encoding="utf-8") as file:
	# Reading the contents of a file
	content = file.read()
	# Replace the desired part of the text using the replace method
	new_content = content.replace('!!{PLACEHOLDER}!!', tag)
	# Move the file pointer to the beginning (0) to overwrite
	file.seek(0)
	# Write the changed content back to the file
	file.write(new_content)
	# Trim the file if the new content is shorter than the old one to remove the remaining data
	file.truncate()
print("[TAG MARKER] DONE")

# - Mark src/clipman/__version__.py
print("[TAG MARKER] MARKING VERSION IN src/clipman/__version__.py")
with open('src/clipman/__version__.py', 'r+', encoding="utf-8") as file:
	# Reading the contents of a file
	content = file.read()
	# Replace the desired part of the text using the replace method
	new_content = content.replace('!!{PLACEHOLDER}!!', tag)
	# Move the file pointer to the beginning (0) to overwrite
	file.seek(0)
	# Write the changed content back to the file
	file.write(new_content)
	# Trim the file if the new content is shorter than the old one to remove the remaining data
	file.truncate()
print("[TAG MARKER] DONE")

print("[TAG MARKER] Marking complete")
