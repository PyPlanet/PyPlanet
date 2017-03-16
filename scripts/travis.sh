#!/usr/bin/env bash
BEFORE_PWD=`pwd`
cd "$(dirname "$0")"

ROOT=`realpath "../"`

# This script will initiate configuration files for Travis-CI Test Environment.
cp -n travis/settings/* ${ROOT}/settings/

##########
cd $BEFORE_PWD
