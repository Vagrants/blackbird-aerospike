%define _unpackaged_files_terminate_build 0
%define name blackbird-aerospike
%define version 0.1.2
%define unmangled_version 0.1.2
%define release 1

%define blackbird_conf_dir /etc/blackbird/conf.d

Summary: Get aerospike information.
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: makocchi <makocchi@gmail.com>
Packager: makocchi <makocchi@gmail.com>
Requires: blackbird
Url: https://github.com/Vagrants/blackbird-aerospike
BuildRequires:  python-devel

%description
Project Info
============

* Project Page: https://github.com/Vagrants/blackbird-aerospike


%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --skip-build --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/%{blackbird_conf_dir}
cp -p aerospike.cfg $RPM_BUILD_ROOT/%{blackbird_conf_dir}/aerospike.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Wed Jul 29 2015 makocchi <makocchi@gmail.com> - 0.1.2-1
- fix latency cmd

* Tue Jul  7 2015 makocchi <makocchi@gmail.com> - 0.1.1-1
- add aerospike python library path

* Wed Dec 25 2014 makocchi <makocchi@gmail.com> - 0.1.0-1
- first package
