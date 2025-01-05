%define _unpackaged_files_terminate_build 1

%define api_version ASSERT
%define minor_version ASSERT
%define gir_name ASSERT-%api_version

Name: ASSERT-%api_version
Version: %api_version-%minor_version
Release: alt1

Summary: ASSERT
License: GPL-3.0-or-later
Group: ASSERT
Url: ASSERT
Vcs: ASSERT.git

Source0: %name-%version.tar

BuildRequires (pre): 
BuildRequires: 

%description
%summary.

%package devel
Summary: Development files for %name
Group: Development/C

Requires: %name = %EVR

%description devel
%summary.

%package devel-vala
Summary: Development vapi files for %name
Group: System/Libraries
BuildArch: noarch

Requires: %name = %EVR

%description devel-vala
%summary.

%package gir
Summary: Typelib files for %name
Group: System/Libraries

Requires: %name = %EVR

%description gir
%summary.

%package gir-devel
Summary: Development gir files for %name for various bindings
Group: Development/Other
BuildArch: noarch

Requires: %name = %EVR

%description gir-devel
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
%_libdir/%name.so.*
%doc README.md

%files devel
%_libdir/%name.so
%_includedir/%name.h
%_pkgconfigdir/%name.pc

%files devel-vala
%_vapidir/%name.vapi
%_vapidir/%name.deps

%files gir
%_typelibdir/%gir_name.typelib

%files gir-devel
%_girdir/%gir_name.gir
