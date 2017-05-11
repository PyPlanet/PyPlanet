#!/bin/sh
#
# Download and run the latest release version of the PyPlanet client.
#

# Make it possible to use `sh script.sh`
set -e

# Support for busybox and others where there is no "command",
# but "which" instead
if command -v command > /dev/null 2>&1 ; then
  export EXISTS="command -v"
elif which which > /dev/null 2>&1 ; then
  export EXISTS="which"
else
  error "Cannot find command nor which... please install one!"
  exit 1
fi

if test "`id -u`" -ne "0" ; then
  if $EXISTS sudo 1>/dev/null 2>&1; then
    SUDO=sudo
  else
    say \"sudo\" is not available, will use \"su\" for installation steps...
    SUDO=su_sudo
  fi
else
  SUDO=
fi

# Determinate platform, os and distro.

machine=`uname -m`
os=`uname -s`

if test -f "/etc/lsb-release" && grep -q DISTRIB_ID /etc/lsb-release && ! grep -q wrlinux /etc/lsb-release; then
  platform=`grep DISTRIB_ID /etc/lsb-release | cut -d "=" -f 2 | tr '[A-Z]' '[a-z]'`
  platform_version=`grep DISTRIB_RELEASE /etc/lsb-release | cut -d "=" -f 2`

  if test "$platform" = "\"cumulus linux\""; then
    platform="cumulus_linux"
  elif test "$platform" = "\"cumulus networks\""; then
    platform="cumulus_networks"
  fi

elif test -f "/etc/debian_version"; then
  platform="debian"
  platform_version=`cat /etc/debian_version`
elif test -f "/etc/Eos-release"; then
  # EOS may also contain /etc/redhat-release so this check must come first.
  platform=arista_eos
  platform_version=`awk '{print $4}' /etc/Eos-release`
  machine="i386"
elif test -f "/etc/redhat-release"; then
  platform=`sed 's/^\(.\+\) release.*/\1/' /etc/redhat-release | tr '[A-Z]' '[a-z]'`
  platform_version=`sed 's/^.\+ release \([.0-9]\+\).*/\1/' /etc/redhat-release`

  # If /etc/redhat-release exists, we act like RHEL by default
  if test "$platform" = "fedora"; then
    # Change platform version for use below.
    platform_version="6.0"
  fi

  if test "$platform" = "xenserver"; then
    # Current XenServer 6.2 is based on CentOS 5, platform is not reset to "el" server should hanlde response
    platform="xenserver"
  else
    platform="el"
  fi

elif test -f "/etc/system-release"; then
  platform=`sed 's/^\(.\+\) release.\+/\1/' /etc/system-release | tr '[A-Z]' '[a-z]'`
  platform_version=`sed 's/^.\+ release \([.0-9]\+\).*/\1/' /etc/system-release | tr '[A-Z]' '[a-z]'`
  # amazon is built off of fedora, so act like RHEL
  if test "$platform" = "amazon linux ami"; then
    platform="el"
    platform_version="6.0"
  fi
# Apple OS X
elif test -f "/usr/bin/sw_vers"; then
  platform="mac_os_x"
  # Matching the tab-space with sed is error-prone
  platform_version=`sw_vers | awk '/^ProductVersion:/ { print $2 }' | cut -d. -f1,2`

  # x86_64 Apple hardware often runs 32-bit kernels (see OHAI-63)
  x86_64=`sysctl -n hw.optional.x86_64`
  if test $x86_64 -eq 1; then
    machine="x86_64"
  fi
elif test -f "/etc/release"; then
  machine=`/usr/bin/uname -p`
  if grep -q SmartOS /etc/release; then
    platform="smartos"
    platform_version=`grep ^Image /etc/product | awk '{ print $3 }'`
  else
    platform="solaris2"
    platform_version=`/usr/bin/uname -r`
  fi
elif test -f "/etc/SuSE-release"; then
  if grep -q 'Enterprise' /etc/SuSE-release;
  then
      platform="sles"
      platform_version=`awk '/^VERSION/ {V = $3}; /^PATCHLEVEL/ {P = $3}; END {print V "." P}' /etc/SuSE-release`
  else
      platform="suse"
      platform_version=`awk '/^VERSION =/ { print $3 }' /etc/SuSE-release`
  fi
elif test "x$os" = "xFreeBSD"; then
  platform="freebsd"
  platform_version=`uname -r | sed 's/-.*//'`
elif test "x$os" = "xAIX"; then
  platform="aix"
  platform_version="`uname -v`.`uname -r`"
  machine="powerpc"
fi

if test "x$platform" = "x"; then
  echo "Unable to determine platform version!"
  report_bug
  exit 1
fi

# Install dependencies.
if [ "$platform" = "ubuntu" ] || [ "$platform" = "debian" ]; then
  $SUDO apt-get update || error apt-get update hit problems but continuing anyway...
  $SUDO apt-get install python python3 python3-dev virtualenv build-essential libssl-dev libffi-dev python3-pip zlib1g-dev

fi

echo "You are now ready to continue step 1 of the installation manual"
echo "More information: http://pypla.net/"
exit
