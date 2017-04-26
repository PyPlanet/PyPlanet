#!/usr/bin/env bash

# Check if we should run at all
if [[ ${TOXENV} == *"integration"* ]]; then
  echo "Integration test requires the dedicated server.. Downloading..."
else
  exit 0
fi

BEFORE_PWD=`pwd`
cd "$(dirname "$0")"
cd ../../
# From now we are in the project root.

# Download the latest dedicated server.
wget http://files.maniaplanet.com/ManiaPlanet3Beta/ManiaPlanetBetaServer_latest.zip -O ./dedicated.zip

# Unzip the dedicated into the subdirectory.
mkdir -p ./dedicated
unzip dedicated.zip -d ./dedicated

# Prepare configuration files.
cp tests/_scripts/travis/dedicated/dedicated_cfg.txt dedicated/UserData/Config/dedicated_cfg.txt
cp tests/_scripts/travis/dedicated/matchsettings_1.txt dedicated/UserData/Maps/MatchSettings/matchsettings_1.txt

##########
cd $BEFORE_PWD
