#!/usr/bin/env bash
BEFORE_PWD=`pwd`
cd "$(dirname "$0")"
cd ../..
# From now we are in the project root.

# Download the latest dedicated server.
wget http://files.maniaplanet.com/ManiaPlanet3Beta/ManiaPlanetBetaServer_latest.zip -O ./dedicated.zip

# Unzip the dedicated into the subdirectory.
mkdir -p ./dedicated
unzip dedicated.zip -d ./dedicated

# Prepare configuration files.
cp scripts/travis/dedicated/dedicated_cfg.txt dedicated/UserData/Config/dedicated_cfg.txt
cp scripts/travis/dedicated/matchsettings_1.txt dedicated/UserData/Maps/MatchSettings/matchsettings_1.txt

##########
cd $BEFORE_PWD
