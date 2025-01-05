%define _unpackaged_files_terminate_build 1

Name: ASSERT
Version: ASSERT
Release: alt1

Summary: ASSERT
License: GPL-3.0-or-later
Group: ASSERT
Url: ASSERT
Vcs: ASSERT.git

Source0: %name-%version.tar

BuildRequires(pre): 
BuildRequires: 

%description
%summary.

%prep
%setup

%build
%meson
%meson_build

%install
%meson_install
%find_lang %name --with-gnome

%check
%meson_test

%files -f %name.lang
%_bindir/%name
%doc README.md
