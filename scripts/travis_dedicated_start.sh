#!/usr/bin/env bash
BEFORE_PWD=`pwd`
cd "$(dirname "$0")"
cd ..
cd dedicated

# Start the dedicated server.
./ManiaPlanetServer /dedicated_cfg=dedicated_cfg.txt /game_settings=MatchSettings/matchsettings_1.txt /login=${MP_USER} /password=${MP_PASS} /loadcache
# Make sure we exit with non-zero code on error
if [ $? -ne 0 ]; then
  echo "Starting failed!"
  exit 10
fi

# Sleep 10 seconds to let the server boot.
sleep 10

##########
cd $BEFORE_PWD
