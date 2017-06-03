#!/usr/bin/env bash

# Check if we should run at all
if [[ ${TOXENV} == *"integration"* ]]; then
  echo "Integration test requires the dedicated server.. Starting..."
else
  exit 0
fi
# Check if we should use the second dedicated account instead.
if [[ ${TOXENV} == *"py36-integration"* ]]; then
  MP_USER="${MP_USER}2"
fi


BEFORE_PWD=`pwd`
cd "$(dirname "$0")"
cd ../../dedicated

# Start the dedicated server.
./ManiaPlanetServer /dedicated_cfg=dedicated_cfg.txt /title=TMCanyon /game_settings=MatchSettings/matchsettings_1.txt /login=${MP_USER} /password=${MP_PASS} /loadcache
# Make sure we exit with non-zero code on error
if [ $? -ne 0 ]; then
  echo "Starting failed!"
  exit 10
fi

# Sleep 10 seconds to let the server boot.
sleep 10

##########
cd $BEFORE_PWD
