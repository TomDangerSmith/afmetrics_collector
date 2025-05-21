# !!! This spec file is deprecated !!! please build the package with 'python3 setup.py bdist_rpm' instead of doing this !!!

Name:		afmetrics-collector
Version:	1
Release:	1
Summary:	Analysis facility metrics collector

#Group:		
License:	MIT
URL:		https://github.com/TomDangerSmith/afmetrics_collector
#Source0:	

BuildRequires:	python3, python3-pip, python3-devel, gcc
Requires:	python3, python3-pip, python3-devel, gcc

%description
UChicago developed, Brookhaven National Lab modified program for collecting batch, ssh, and jupyter metrics for sending to a logstash server

%define NVdir	%{name}-%{version}

%prep
rm -rf %{NVdir}
git clone %{url}.git %{NVdir}
cd %{NVdir}
git checkout BNL-production

%build

%install
mkdir -p %{buildroot}/root/afmetrics
cp -ra %{NVdir}/. %{buildroot}/root/afmetrics

%pre
pip3 install -U setuptools==70 setuptools_scm wheel importlib_metadata psutil requests kubernetes

%post
cd /root/afmetrics
python3 setup.py bdist_wheel
pip3 install /root/afmetrics/dist/afmetrics*.whl

%files
%attr(-, root, root) /root/afmetrics

%clean

%changelog

%postun
pip3 uninstall -y afmetrics_collector
rm -rf /root/afmetrics
