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
wget http://files.v04.maniaplanet.com/server/ManiaplanetServer_2017-05-02.zip -O ./dedicated.zip
# wget http://files.maniaplanet.com/ManiaPlanet3Beta/ManiaPlanetBetaServer_latest.zip -O ./dedicated.zip

# Unzip the dedicated into the subdirectory.
mkdir -p ./dedicated
unzip dedicated.zip -d ./dedicated

# Download titles.
wget https://v4.live.maniaplanet.com/ingame/public/titles/download/TMStadium@nadeo.Title.Pack.gbx -O ./dedicated/UserData/Packs/TMCanyon@nadeo.Title.Pack.gbx

# Prepare configuration files.
cp tests/_scripts/travis/dedicated/dedicated_cfg.txt dedicated/UserData/Config/dedicated_cfg.txt
cp tests/_scripts/travis/dedicated/matchsettings_1.txt dedicated/UserData/Maps/MatchSettings/matchsettings_1.txt

##########
cd $BEFORE_PWD
