import subprocess
import os

os.system("tree -a")
os.system("git fetch --tags")
tag = subprocess.check_output("git describe --tags", shell=True, encoding="UTF-8")

print("[TAG MARKER] git response: " + tag)
tag = tag.replace("\n", "").replace("v", "")
if tag.find("-") > 1:
	tag = tag[0:tag.find("-")]
print("[TAG MARKER] FOUND TAG: " + tag)

print("[TAG MARKER] MARKING VERSION IN pyproject.toml")
# Open the file for reading and writing (the 'r+' mode provides both read and write access)
with open('pyproject.toml', 'r+') as file:
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

print("[TAG MARKER] MARKING VERSION IN src/clipman/__version__.py")
with open('src/clipman/__version__.py', 'r+') as file:
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

print("[TAG MARKER] Work finished")
