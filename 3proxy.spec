%global _hardened_build 1

Name:		3proxy
Version:	0.8.2
Release:	1
Summary:	Tiny but very powerful proxy
License:	BSD or ASL 2.0 or GPLv2+ or LGPLv2+
Group:		Networking/Other
Url:		http://3proxy.ru/?l=EN
Source0:	https://github.com/z3APA3A/%{name}/archive/%{name}-%{version}.tar.gz
Source2:	3proxy.cfg
Source3:	3proxy.service
BuildRequires:	openssl-devel
Patch0:		3proxy-0.6.1-config-path.patch
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd

%description
%{name} -- light proxy server.
Universal proxy server with HTTP, HTTPS, SOCKS v4, SOCKS v4a, SOCKS v5, FTP,
POP3, UDP and TCP portmapping, access control, bandwith control, traffic
limitation and accounting based on username, client IP, target IP, day time,
day of week, etc.

%prep
%setup -qn %{name}-%{name}-%{version}

%patch0 -p0 -b .man-cfg

# To use "fedora" CFLAGS (exported)
sed -i -e "s/CFLAGS =/CFLAGS +=/" Makefile.Linux

%build
%make_build -f Makefile.Linux

%install

mkdir -p %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/
mkdir -p %{buildroot}%{_mandir}/man{3,8}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
install -m755 -D src/%{name} %{buildroot}%{_bindir}/%{name}
install -m755 -D src/dighosts %{buildroot}%{_bindir}/dighosts
install -m755 -D src/ftppr %{buildroot}%{_bindir}/ftppr
install -m755 -D src/mycrypt %{buildroot}%{_bindir}/mycrypt
install -m755 -D src/pop3p %{buildroot}%{_bindir}/pop3p
install -m755 -D src/%{name} %{buildroot}%{_bindir}/%{name}
install -m755 -D src/proxy %{buildroot}%{_bindir}/htproxy
install -m755 -D src/socks %{buildroot}%{_bindir}/socks
install -m755 -D src/tcppm %{buildroot}%{_bindir}/tcppm
install -m755 -D src/udppm %{buildroot}%{_bindir}/udppm

install -pD -m644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/%{name}.cfg
install -pD -m755 %{SOURCE3} %{buildroot}/%{_unitdir}/%{name}.service

	for man in man/*.{3,8} ; do
	install "$man" "%{buildroot}%{_mandir}/man${man:(-1)}/"
	done

cat > %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/40-%{name} <<EOF
#!/bin/sh

	if [ "\$2" = "up" ]; then
	/sbin/service %{name} condrestart || : # reload doesn't work
	fi
EOF

%clean

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/%{name}.cfg
%attr(0755,root,root) %config %{_sysconfdir}/NetworkManager/dispatcher.d/40-%{name}
%{_localstatedir}/log/%{name}
%doc README authors copying Release.notes
%{_mandir}/man8/*.8*
%{_mandir}/man3/*.3*
%{_unitdir}/%{name}.service
