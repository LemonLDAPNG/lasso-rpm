%global with_java 1
%global with_php 1
%global with_perl 1
%global with_python 1
%global with_wsf 0

%if %{with_php}
%if "%{php_version}" < "5.6"
%global ini_name     %{name}.ini
%else
%global ini_name     40-%{name}.ini
%endif
%endif

Summary: Liberty Alliance Single Sign On
Name: lasso
Version: 2.7.0
Release: 1%{?dist}
License: GPLv2+
Group: System Environment/Libraries
Source: http://dev.entrouvert.org/lasso/lasso-%{version}.tar.gz
%if %{with_wsf}
BuildRequires: cyrus-sasl-devel
%endif
BuildRequires: gtk-doc, libtool-ltdl-devel
BuildRequires: glib2-devel, swig
BuildRequires: libxml2-devel, xmlsec1-devel, openssl-devel, xmlsec1-openssl-devel
Url: http://lasso.entrouvert.org/

%description
Lasso is a library that implements the Liberty Alliance Single Sign On
standards, including the SAML and SAML2 specifications. It allows to handle
the whole life-cycle of SAML based Federations, and provides bindings
for multiple languages.

%package devel
Summary: Lasso development headers and documentation
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the header files, static libraries and development
documentation for Lasso.

%if %{with_perl}
%package perl
Summary: Liberty Alliance Single Sign On (lasso) Perl bindings
Group: Development/Libraries
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(Test::More)
BuildRequires: perl(Error)
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires: %{name}%{?_isa} = %{version}-%{release}

%description perl
Perl language bindings for the lasso (Liberty Alliance Single Sign On) library.
%endif

%if %{with_java}
%package java
Summary: Liberty Alliance Single Sign On (lasso) Java bindings
Group: Development/Libraries
BuildRequires: java-devel
BuildRequires: jpackage-utils
Requires: java-headless
Requires: jpackage-utils
Requires: %{name}%{?_isa} = %{version}-%{release}

%description java
Java language bindings for the lasso (Liberty Alliance Single Sign On) library.
%endif

%if %{with_php}
%package php
Summary: Liberty Alliance Single Sign On (lasso) PHP bindings
Group: Development/Libraries
BuildRequires: php-devel, expat-devel
BuildRequires: python2
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}
Provides: php-lasso = %{version}-%{release}
Provides: php-lasso%{?_isa} = %{version}-%{release}

%description php
PHP language bindings for the lasso (Liberty Alliance Single Sign On) library.
%endif

%if %{with_python}
%package python
Summary: Liberty Alliance Single Sign On (lasso) Python bindings
Group: Development/Libraries
%if 0%{?rhel} == 8
BuildRequires: python3-devel
BuildRequires: python3-lxml, python3-six
%define __python /usr/bin/python3
%else
BuildRequires: python2-devel
BuildRequires: python-lxml, python-six
%endif
Requires: python
Requires: %{name}%{?_isa} = %{version}-%{release}

%description python
Python language bindings for the lasso (Liberty Alliance Single Sign On)
library.
%endif

%prep
%setup -q -n %{name}-%{version}

%build
./autogen.sh
%configure --prefix=%{_prefix} \
%if !%{with_java}
           --disable-java \
%endif
%if !%{with_python}
           --disable-python \
%endif
%if !%{with_perl}
           --disable-perl \
%endif
%if %{with_php}
%if 0%{?rhel} > 7
           --enable-php7=yes \
           --with-php7-config=/usr/bin/php-config \
           --with-php7-config-dir=%{php_inidir} \
%else
           --enable-php5=yes \
           --with-php5-config-dir=%{php_inidir} \
%endif
%else
           --enable-php5=no \
           --enable-php7=no \
%endif
%if %{with_wsf}
           --enable-wsf \
           --with-sasl2=%{_prefix}/sasl2 \
%endif
#           --with-html-dir=%{_datadir}/gtk-doc/html

make %{?_smp_mflags} CFLAGS="%{optflags}"

%check
export LD_LIBRARY_PATH="%{_builddir}/%{buildsubdir}/lasso/.libs"
make check

%install
#install -m 755 -d %{buildroot}%{_datadir}/gtk-doc/html

make install exec_prefix=%{_prefix} DESTDIR=%{buildroot}
find %{buildroot} -type f -name '*.la' -exec rm -f {} \;
find %{buildroot} -type f -name '*.a' -exec rm -f {} \;

# Perl subpackage
%if %{with_perl}
find %{buildroot} \( -name perllocal.pod -o -name .packlist \) -exec rm -v {} \;

find %{buildroot}/usr/lib*/perl5 -type f -print |
        sed "s@^%{buildroot}@@g" > %{name}-perl-filelist
if [ "$(cat %{name}-perl-filelist)X" = "X" ] ; then
    echo "ERROR: EMPTY FILE LIST"
    exit -1
fi
%endif

# PHP subpackage
%if %{with_php}
install -m 755 -d %{buildroot}%{_datadir}/php/%{name}
mv %{buildroot}%{_datadir}/php/lasso.php %{buildroot}%{_datadir}/php/%{name}

# rename the PHP config file when needed (PHP 5.6+)
if [ "%{name}.ini" != "%{ini_name}" ]; then
  mv %{buildroot}%{php_inidir}/%{name}.ini \
     %{buildroot}%{php_inidir}/%{ini_name}
fi
%endif

# Remove bogus doc files
rm -fr %{buildroot}%{_defaultdocdir}/%{name}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%{_libdir}/liblasso.so.*
%doc AUTHORS COPYING NEWS README

%files devel
%defattr(-,root,root)
%{_libdir}/liblasso.so
%{_libdir}/pkgconfig/lasso.pc
%{_includedir}/%{name}

%if %{with_perl}
%files perl -f %{name}-perl-filelist
%defattr(-,root,root)
%endif

%if %{with_java}
%files java
%defattr(-,root,root)
%{_libdir}/java/libjnilasso.so
%{_javadir}/lasso.jar
%endif

%if %{with_php}
%files php
%defattr(-,root,root)
%attr(755,root,root) %{php_extdir}/lasso.so
%config(noreplace) %attr(644,root,root) %{php_inidir}/%{ini_name}
%attr(755,root,root) %dir %{_datadir}/php/%{name}
%attr(644,root,root) %{_datadir}/php/%{name}/lasso.php
%endif

%if %{with_python}
%files python
%defattr(-,root,root)
%{python_sitearch}/lasso.py*
%{python_sitearch}/_lasso.so
%if 0%{?rhel} == 8
%{python_sitearch}/__pycache__/*
%endif
%endif

%changelog
* Tue Jun 01 2021 Clement Oudot <clem.oudot@gmail.com> - 2.7.0-1
- New upstream relase 2.7.0

* Mon Apr 27 2020 Clement Oudot <clem.oudot@gmail.com> - 2.6.1-1
- New upstream relase 2.6.1

* Mon Jun 18 2018 Clement Oudot <clem.oudot@gmail.com> - 2.6.0-1
- New upstream relase 2.6.0

* Fri Feb 19 2016 Clement Oudot <clem.oudot@gmail.com> - 2.5.1-1
- New upstream relase 2.5.1

* Fri Sep 04 2015 Clement Oudot <clem.oudot@gmail.com> - 2.5.0-1
- New upstream relase 2.5.0

* Mon May 04 2015 Clement Oudot <clem.oudot@gmail.com> - 2.4.1-3
- Fix tests for Perl bindings

* Fri Jan 23 2015 Simo Sorce <simo@redhat.com> - 2.4.1-2
- Enable perl bindings

* Thu Aug 28 2014 Simo Sorce <simo@redhat.com> - 2.4.1-1
- New upstream relase 2.4.1
- Drop patches as they have all been integrated upstream

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 20 2014 Remi Collet <rcollet@redhat.com> - 2.4.0-4
- rebuild for https://fedoraproject.org/wiki/Changes/Php56
- add numerical prefix to extension configuration file
- drop unneeded dependency on pecl
- add provides php-lasso

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 25 2014 Simo Sorce <simo@redhat.com> - 2.4.0-2
- Fixes for arches where pointers and integers do not have the same size
  (ppc64, s390, etc..)

* Mon Apr 14 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 2.4.0-1
- Use OpenJDK instead of GCJ for java bindings

* Sat Jan 11 2014 Simo Sorce <simo@redhat.com> 2.4.0-0
- Update to final 2.4.0 version
- Drop all patches, they are now included in 2.4.0
- Change Source URI

* Mon Dec  9 2013 Simo Sorce <simo@redhat.com> 2.3.6-0.20131125.5
- Add patches to fix rpmlint license issues
- Add upstream patches to fix some build issues

* Thu Dec  5 2013 Simo Sorce <simo@redhat.com> 2.3.6-0.20131125.4
- Add patch to support automake-1.14 for rawhide

* Mon Nov 25 2013 Simo Sorce <simo@redhat.com> 2.3.6-0.20131125.3
- Initial packaging
- Based on the spec file by Jean-Marc Liger <jmliger@siris.sorbonne.fr>
- Code is updated to latest master via a jumbo patch while waiting for
  official upstream release.
- Jumbo patch includes also additional patches sent to upstream list)
  to build on Fedora 20
- Perl bindings are disabled as they fail to build
- Disable doc building as it doesn't ork correctly for now
