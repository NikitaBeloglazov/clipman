#  * - = - = - =
#  * spec file for package CLIPMAN
#  * - = - = - =
#  * Copyright (C) 2023-2024 Nikita Beloglazov <nnikita.beloglazov@gmail.com>
#  *
#  * This file is part of github.com/NikitaBeloglazov/clipman.
#  *
#  * NikitaBeloglazov/clipman is free software; you can redistribute it and/or
#  * modify it under the terms of the Mozilla Public License 2.0
#  * published by the Mozilla Foundation.
#  *
#  * NikitaBeloglazov/clipman is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY.
#  *
#  * You should have received a copy of the Mozilla Public License 2.0
#  * along with NikitaBeloglazov/clipman
#  * If not, see https://mozilla.org/en-US/MPL/2.0.
#  * - = - = - =
#  * Please submit bugfixes or comments via https://github.com/NikitaBeloglazov/clipman/issues
#  * - = - = - =

%{?!python_module:%define python_module() python-%{**} python3-%{**}}
Name:           clipman
# Version sets dynamically by _service
Version:        0.0.0
Release:        0
Summary:        Python 3 module for working with clipboard. Created because pyperclip is discontinued. Mostly made for YTCON
License:        MPL-2.0
URL:            https://github.com/NikitaBeloglazov/clipman
Source0:        %{name}-%{version}.tar
BuildRequires:  python-rpm-macros
BuildRequires:  %{python_module setuptools}
BuildRequires:  %{python_module setuptools_scm}
BuildRequires:  %{python_module pip}
BuildRequires:  fdupes

Requires:       python

# - = KDE
Requires:       python-dbus_next
# - = X11
Requires:       xsel
Recommends:     xclip
# - = Wayland
Requires:       wl-clipboard

BuildArch:      noarch
%python_subpackages

%description
Python 3 module for working with clipboard. Created because pyperclip is discontinued. Mostly made for YTCON. More at https://github.com/NikitaBeloglazov/clipman

%prep
echo "DEBUG - PREP RUNNING"
%autosetup -p1 -n clipman-%{version}

%build
echo "DEBUG - BUILD RUNNING"
export SETUPTOOLS_SCM_PRETEND_VERSION="v%{version}"
%pyproject_wheel

%install
echo "DEBUG - INSTALL RUNNING"
%pyproject_install
%python_expand %fdupes %{buildroot}%{$python_sitelib}

%files %{python_files}
%{python_sitelib}/clipman
%{python_sitelib}/clipman-%{version}.dist-info
%license LICENSE
%doc README.md

%changelog
