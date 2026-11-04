#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/../_files/server"

# Start the dedicated server.
./ManiaPlanetServer /dedicated_cfg=dedicated_cfg.txt /title=TMCanyon@nadeo /game_settings=MatchSettings/matchsettings_1.txt /login=$MP_USER /password=$MP_PASS

# Sleep 10 seconds to let the server boot.
sleep 10
