%define _unpackaged_files_terminate_build 1
%define app_id ASSERT

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
%{?_enable_check:BuildRequires: /usr/bin/appstreamcli desktop-file-utils}

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
export AS_VALIDATE_NONET="true"
%meson_test

%files -f %name.lang
%_bindir/%name
%_datadir/metainfo/%app_id.metainfo.xml
%_datadir/glib-2.0/schemas/%app_id.gschema.xml
%_desktopdir/%app_id.desktop
%_iconsdir/hicolor/*/apps/*.svg
%doc README.md
