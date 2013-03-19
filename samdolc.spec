
%define		mainver		0.1

Name:		samdolc
Version:	%{mainver}
Release:	4
License:	Multiple, each package has their license
Summary:	My own bookmarking tool for recruit
Group:		Internet

URL:		https://github.com/ptmono/samdol
Source0:	%{name}-%{mainver}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:	noarch
BuildRequires: python2-devel, systemd-units
Requires:	PyQt4, mongodb, mongodb-server, python-pip, python-setuptools, libxml2-devel, python-lxml, python-virtualenv

%description
My won bookmarking tool for recruit. Currently it support http://www.saramin.co.kr, http://www.work.go.kr.

%prep
%setup -c


%build

%pre
# Stop service before remove or upgrade
echo "start"
if [ "$1" = 0 ] || [ "$1" -ge 2 ]; then
echo "start in"
systemctl stop samdolc.service
fi


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir_p} $RPM_BUILD_ROOT%{_prefix}

%{__python} install.py \
    --dir \
    $RPM_BUILD_ROOT%{_prefix} \
    install


%clean
%{__rm} -rf $RPM_BUILD_ROOT


%post
cd $RPM_BUILD_ROOT%{_datadir}/samdolc

%{__python} install.py \
    --dir \
    $RPM_BUILD_ROOT%{_prefix} \
    install_chrome_extension

%{__chmod} 744 init_virtualenv.sh
./init_virtualenv.sh

# Install service On first install
if [ "$1" = 1 ]; then
%{__python} install.py \
    --dir \
    $RPM_BUILD_ROOT%{_prefix} \
    install_service
fi


# Restart service after first install and upgrade
if [ "$1" = 1 ] || [ "$1" -ge 2 ]; then
systemctl --system daemon-reload
systemctl enable samdolc.service > /dev/null 2>&1
systemctl start samdolc.service
fi

%preun
# Remove created files and service on remove lastest version
if [ "$1" = 0 ]; then
[ -f /etc/init.d/samdolc ] && \
    systemctl stop samdolc.service; \
    systemctl disable samdolc.service; \
    %{__rm} /etc/init.d/samdolc

[ -d $RPM_BUILD_ROOT%{_datadir}/samdolc ] && \
    %{__rm} -rf $RPM_BUILD_ROOT%{_datadir}/samdolc/server; \
    %{__rm} -rf $RPM_BUILD_ROOT%{_datadir}/samdolc/include; \
    %{__rm} -rf $RPM_BUILD_ROOT%{_datadir}/samdolc/bin; \
    %{__rm} -rf $RPM_BUILD_ROOT%{_datadir}/samdolc/lib; \
    %{__rm} $RPM_BUILD_ROOT%{_datadir}/samdolc/lib64

[ -f /opt/google/chrome/extensions/onpobpkjhjihnhmjpjemcedjebllieoi.json ] && \
    %{__rm} /opt/google/chrome/extensions/onpobpkjhjihnhmjpjemcedjebllieoi.json
fi

%files
%defattr(-,root,root, -)

%{_datadir}/%{name}/


%changelog
* Tue Mar 19 2013 ptmono <ptmono@gmail.com> 0.1-4
- Added permanent recruit view

* Fri Feb  8 2013 ptmono <ptmono@gmail.com> 0.1-3
- Fixed upgrade problem of rpm

* Fri Feb  8 2013 ptmono <ptmono@gmail.com> 0.1-2
- Support work.go.kr
- Bloker class is added
