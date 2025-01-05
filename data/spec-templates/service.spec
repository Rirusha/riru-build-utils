%define _unpackaged_files_terminate_build 1

Name: ASSERT
Version: ASSERT
Release: alt1

Summary: ASSERT
License: GPL-3.0-or-later
Group: ASSERT
Url: ASSERT
Vcs: ASSERT.git

Source: %name-%version.tar

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

%check
%meson_test

%files
%_bindir/%name
%_user_unitdir/%name.service
%doc README.md
