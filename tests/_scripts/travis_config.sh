#!/usr/bin/env bash
BEFORE_PWD=`pwd`
cd "$(dirname "$0")"

# This script will initiate configuration files for Travis-CI Test Environment.
cp -n travis/settings/* ../../settings/

##########
cd $BEFORE_PWD
