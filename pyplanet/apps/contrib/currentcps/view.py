import math

from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.utils import times
import logging


class CPWidgetView(TimesWidgetView):
    widget_x = -160
    widget_y = 70.5
    z_index = 130
    size_x = 38
    size_y = 55.5
    title = 'Current CPs'

    template_name = 'currentcps/cpwidget.xml'

    def __init__(self, app, height=55.5):
        super().__init__(self)
        self.app = app
        self.manager = app.context.ui
        self.id = 'pyplanet__widgets_currentcps'

        self.size_y = height

    def set_num_cps(self, num_cps=None):
        if not num_cps:
            self.title = 'Current CPs'
        else:
            self.title = 'Current CPs $aaa/ {}'.format(num_cps)

    async def get_player_data(self):
        data = await super().get_player_data()

        # Calculate the maximum number of rows that can be displayed
        max_n = math.floor((self.size_y - 5.5) / 3.3)

        # Maps a logon to the data that should be displayed
        cps = {}

        for idx, player in enumerate(self.app.instance.player_manager.online):
            last_fin = 0
            list_times = []
            n = 1
            for pcp in self.app.player_cps:
                # Make sure to only display a certain number of entries
                if float(n) >= max_n:
                    break

                # Set time color to green for your own CP time
                list_time = {'index': n, 'color': "$0f3" if player.login == pcp.player.login else "$bbb"}

                # Display 'fin' when the player crossed the finish line else display the CP number
                if pcp.cp == -1 or (pcp.cp == 0 and pcp.time != 0):
                    list_time['cp'] = 'fin'
                    last_fin += 1
                else:
                    list_time['cp'] = str(pcp.cp)

                list_time['cptime'] = times.format_time(pcp.time)
                list_time['nickname'] = pcp.player.nickname
                list_time['login'] = pcp.player.login

                # Only show top 5 fins but always show the current player
                if (pcp.cp == -1 or (pcp.cp == 0 and pcp.time != 0)) and last_fin > 5:
                    if player.login != pcp.player.login:
                        continue
                    list_times[4] = list_time
                    continue

                list_times.append(list_time)
                n += 1
            cps[player.login] = {'cps': list_times}

        data.update(cps)

        return data

    async def get_context_data(self):
        self.widget_y = 12.5 if self.app.dedimania_enabled else 70.5
        return await super().get_context_data()

    async def handle_catch_all(self, player, action, values, **kwargs):
        logging.debug("CatchAll: " + player.login + ": " + action)
        if str(action).startswith('spec_'):
            target = action[5:]
            await self.app.spec_player(player=player, target_login=target)
