%define oname saxon

Summary:        Java XPath, XSLT 2.0 and XQuery implementation
Name:           %{oname}9
Version:        9.2.0.3
Release:        %mkrel 5
# net.sf.saxon.om.XMLChar is from ASL-licensed Xerces
License:        MPL
Group:          Development/Java
URL:            https://saxon.sourceforge.net/
Source0:        http://dl.sourceforge.net/project/saxon/Saxon-HE/9.2/saxon-resources9-2-0-2.zip
# There's no 9.2.0.3 resource bundle, we patch 9.2.0.2 with difference against 9.2.0.3 source bundle
Patch0:         saxon-9.2.0.2-9.2.0.3.patch
Source1:        %{oname}.saxon.script
Source2:        %{oname}.saxonq.script
Source3:        %{oname}.build.script
Source4:        %{oname}.1
Source5:        %{oname}q.1
BuildRequires:	java-rpmbuild
BuildRequires:  unzip
BuildRequires:  ant
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  bea-stax-api
BuildRequires:  xml-commons-apis
BuildRequires:  xom
BuildRequires:  jdom >= 0:1.0-0.b7
BuildRequires:  java-javadoc
BuildRequires:  jdom-javadoc >= 0:1.0-0.b9.3jpp
BuildRequires:  dom4j
Requires:       jpackage-utils
Requires:       bea-stax-api
Requires:       bea-stax
Requires:       jaxp_parser_impl
Requires:       update-alternatives
Provides:       jaxp_transform_impl = %{version}-%{release}
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Saxon HE is Saxonica's non-schema-aware implementation of the XPath 2.0,
XSLT 2.0, and XQuery 1.0 specifications aligned with the W3C Candidate
Recommendation published on 3 November 2005. It is a complete and
conformant implementation, providing all the mandatory features of
those specifications and nearly all the optional features.

%package manual
Summary:	Manual for %{name}
Group:		Development/Java

%description manual
Manual for %{name}.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

%description javadoc
Javadoc for %{name}.

%package demo
Summary:	Demos for %{name}
Group:		Development/Java
Requires:	%{name} = %{version}-%{release}

%description demo
Demonstrations and samples for %{name}.

%package scripts
Summary:	Utility scripts for %{name}
Group:		Development/Java
Requires:	jpackage-utils >= 0:1.5
Requires:	%{name} = %{version}-%{release}

%description scripts
Utility scripts for %{name}.

%prep
%setup -q -c
unzip -q source.zip -d src
cd src
%patch0 -p1 -b .9.2.0.3
cd ..

cp -p %{SOURCE3} ./build.xml

# deadNET
rm -rf src/net/sf/saxon/dotnet

# Depends on XQJ (javax.xml.xquery)
rm -rf src/net/sf/saxon/xqj

# This requires a EE edition feature (com.saxonica.xsltextn)
rm -rf src/net/sf/saxon/option/sql/SQLElementFactory.java

# cleanup unnecessary stuff we'll build ourselves
rm -rf docs/api
find . \( -name "*.jar" -name "*.pyc" \) -delete

%build
mkdir -p build/classes
cat >build/classes/edition.properties <<EOF
config=net.sf.saxon.Configuration
platform=net.sf.saxon.java.JavaPlatform
EOF

export CLASSPATH=%(build-classpath xml-commons-apis jdom xom bea-stax-api dom4j)
%ant \
  -Dj2se.javadoc=%{_javadocdir}/java \
  -Djdom.javadoc=%{_javadocdir}/jdom

%install
rm -rf %{buildroot}

# jars
mkdir -p %{buildroot}%{_javadir}
cp -p build/lib/%{oname}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
ln -s %{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar

# javadoc
mkdir -p %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr build/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}

# demo
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr samples/* %{buildroot}%{_datadir}/%{name}

# scripts
mkdir -p %{buildroot}%{_bindir}
install -p -m755 %{SOURCE1} %{buildroot}%{_bindir}/%{name}
install -p -m755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}q
mkdir -p %{buildroot}%{_mandir}/man1
install -p -m644 %{SOURCE4} %{buildroot}%{_mandir}/man1/%{name}.1
install -p -m644 %{SOURCE5} %{buildroot}%{_mandir}/man1/%{name}q.1

# jaxp_transform_impl ghost symlink
ln -s %{_sysconfdir}/alternatives \
  %{buildroot}%{_javadir}/jaxp_transform_impl.jar

%clean
rm -rf %{buildroot}

%post
update-alternatives --install %{_javadir}/jaxp_transform_impl.jar \
  jaxp_transform_impl %{_javadir}/%{name}.jar 25

%preun
{
  [ $1 -eq 0 ] || exit 0
  update-alternatives --remove jaxp_transform_impl %{_javadir}/%{name}.jar
} >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%ghost %{_javadir}/jaxp_transform_impl.jar

%files manual
%defattr(-,root,root,-)
%doc doc/*.html

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}-%{version}

%files demo
%defattr(-,root,root,-)
%{_datadir}/%{name}

%files scripts
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_bindir}/%{name}q
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}q.1*
