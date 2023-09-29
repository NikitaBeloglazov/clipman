<!-- # Copyright (c) 2023 Nikita Beloglazov -->
<!-- License: Mozilla Public License 2.0 -->
# ✨ Clipman
[![License: Mozilla Public License 2.0](https://img.shields.io/badge/License:_MPL_2.0-blueviolet?logo=googledocs&logoColor=white&style=for-the-badge)](https://mozilla.org/en-US/MPL/2.0)
[![linting: pylint](https://img.shields.io/badge/Linting:_pylint-success?logo=azurefunctions&logoColor=white&style=for-the-badge)](https://pylint.pycqa.org/en/latest/)
[![maintainer: NikitaBeloglazov](https://img.shields.io/badge/Maintainer:_.%E2%80%A2%C2%B0%E2%97%8F%E2%9D%A4%EF%B8%8F%20NikitaBeloglazov%20Software%20Foundation%20%E2%9D%A4%EF%B8%8F%E2%97%8F%C2%B0%E2%80%A2.-informational?logoColor=white&style=for-the-badge&logo=github)](https://github.com/NikitaBeloglazov)

__Python3 module for working with clipboard. Created because pyperclip is discontinued.__

__Mostly made for [✨ YTCON](https://github.com/NikitaBeloglazov/ytcon)__

# 📘 Features:
* Simple use and simple architecture by KISS
* User-friendly
* No additional modules
* Supports many engines
* We use PyLint and we comment all our code
* Active development

# 👽 Using
```python3
import clipman
clipman.init() # Just initialize module

# Set text to clipboard
clipman.set("test")

# Get text from clipboard. So simple!:)
print(clipman.get())
Out: 'test'
```
__Also you can use `clipman.copy("ytcon")` and `clipman.paste()` as from pyperclip!:)__
## Catching errors
* If you want to catch all errors from the module, use `clipman.exceptions.ClipmanBaseException`:
```python3
import clipman
try:
  clipman.init()
  print(clipman.paste())
except clipman.exceptions.ClipmanBaseException as e:
  print(e)
```
* And if you want to catch specific module error, use its name.

# 🚀 Install
### Clipman is avalible on PyPI - https://pypi.org/project/clipman/

### Install it as pip package
```shell
pip3 install clipman
```

# 📙 Additional deps
__Unstead zypper you need to use system package manager: apt, dnf, pacman, etc__

`- = - = -`
### 🐧 On Linux - X11
- Install `xclip` or `xsel` package

Example: _sudo zypper install xclip_ __OR__ _sudo zypper install xsel_

`- = - = -`
### 🐧 On Linux - Wayland
- Install `wl-clipboard` package

Example: _sudo zypper install wl-clipboard_

`- = - = -`
### 🐸 On Android
Clipboard works only in Termux.
And you need install additional deps in it.
* Install ```Termux:API``` from F-Droid
* Run ```pkg install termux-api```
* Check it - run ```termux-clipboard-get```

# Support
__•‎ 🟩 Linux - FULL SUPPORT, some additional deps needed__

__•‎ 🟩 Android - FULL SUPPORT in Termux, some additional deps needed too__

__•‎ 🟩 Windows - Works natively__

__•‎ 🟥 MacOS - Unsupported, i don't have a Mac 🤷‍♂️. If you have it, and you want to help, [write an issue](https://github.com/NikitaBeloglazov/clipman/issues/new)__

# License
This code is under [Mozilla Public License Version 2.0](/../../blob/main/LICENSE).

# Contribution / Issues
📕 __[!!] If you encouter an error, please read the error text very closely.
The module is specially written so that errors give you a complete answer even if you a lamer__

* 🥼 __Pull requests are welcome!__
* 🌈 Feel free to write Issues! The developer can answer you in the following languages: Ukrainian, English, Russian.
* Don't forget to attach version (`pip3 show clipman`) and error text :)
* ⏩ To speed up the process write to [maintainer](https://github.com/NikitaBeloglazov)
