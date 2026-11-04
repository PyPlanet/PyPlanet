#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/../_files/server"

# Download the latest dedicated server.
wget http://files.v04.maniaplanet.com/server/ManiaplanetServer_2019-10-10.zip -O dedicated.zip
unzip dedicated.zip

# Download titles.
wget https://v4.live.maniaplanet.com/ingame/public/titles/download/TMCanyon@nadeo.Title.Pack.gbx  -P UserData/Packs
