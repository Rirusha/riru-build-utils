%define _unpackaged_files_terminate_build 1

%define shortname rbu
%define snakename riru_build_utils

Name: riru-build-utils
Version: @LAST@
Release: alt1

Summary: Build utilities for Average Rirusha Project
License: GPL-3.0-or-later
Group: Development/Tools
Url: https://github.com/Rirusha/riru-build-utils
Vcs: https://github.com/Rirusha/riru-build-utils.git
BuildArch: noarch

Source: %name-%version.tar

Requires: rpm-utils
Requires: gear
Requires: /usr/bin/ssh
Requires: git

BuildRequires(pre): rpm-macros-meson rpm-build-python3
BuildRequires: meson
BuildRequires: python3-module-paramiko

%description
%summary.

Contains update, test and create commands.

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
%_bindir/%shortname
%python3_sitelibdir_noarch/%snakename/
%_datadir/%name/
