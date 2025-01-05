%define _unpackaged_files_terminate_build 1

Name: ASSERT
Version: ASSERT
Release: alt1

Summary: ASSERT
License: GPL-3.0-or-later
Group: ASSERT
Url: ASSERT
Vcs: ASSERT.git
BuildArch: noarch

Source0: %name-%version.tar

BuildRequires(pre): rpm-macros-meson rpm-build-python3
BuildRequires: meson

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
%python3_sitelibdir_noarch/%name/
