from pyplanet.utils import times
from pyplanet.views.generics.list import ManualListView
from pyplanet.views.generics.widget import TimesWidgetView


class BestCpTimesWidget(TimesWidgetView):
    widget_x = -124.75
    widget_y = 90
    size_x = 250
    size_y = 18
    title = 'Best CPs'

    template_name = 'best_cps/widget_top.xml'

    def __init__(self, app):
        super().__init__(self)
        self.app = app
        self.manager = app.context.ui
        self.id = 'pyplanet__widget_bestcps'
        self.logins = []
        self.action = self.action_cptimeslist

    async def get_player_data(self):
        self.logins = []
        for pcp in self.app.best_cp_times:
            self.logins.append(pcp.player.login)
        data = await super().get_all_player_data(self.logins)
        cps = {}
        for idx, player in enumerate(self.app.instance.player_manager.online):
            list_cps = []
            for pcp in self.app.best_cp_times:
                list_time = {'index': pcp.cp,
                             'color': "$0f3" if player.login == pcp.player.login else "$ff0",
                             'cptime': times.format_time(pcp.time), 'nickname': pcp.player.nickname,
                             'login': pcp.player.login}
                list_cps.append(list_time)
            cps[player.login] = {'cps': list_cps}

        data.update(cps)
        return data

    async def action_cptimeslist(self, player, **kwargs):
        view = CpTimesListView(self.app)
        await view.display(player=player.login)
        return view

    # TODO: remove/rework when finishing widget for rounds/cup/team mode gets reworked
    # Only show the widget in TimeAttack mode as it interferes with UI elements in the other modes
    async def display(self, player=None, **kwargs):
        current_script = await self.app.instance.mode_manager.get_current_script()
        if 'TimeAttack' in current_script:
            await super().display()
        else:
            for idx, player in enumerate(self.app.instance.player_manager.online):
                await super().close(player)


class CpTimesListView(ManualListView):
    title = 'Best CP times in current round'
    icon_style = 'Icons128x128_1'
    icon_substyle = 'Statistics'

    fields = [
        {
            'name': '#',
            'index': 'index',
            'sorting': True,
            'searching': False,
            'width': 10,
            'type': 'label'
        },
        {
            'name': 'Player',
            'index': 'player_nickname',
            'sorting': False,
            'searching': True,
            'width': 70
        },
        {
            'name': 'Time',
            'index': 'record_time',
            'sorting': True,
            'searching': False,
            'width': 30,
            'type': 'label'
        },
    ]

    def __init__(self, app):
        super().__init__(self)
        self.app = app
        self.manager = app.context.ui
        self.provide_search = False

    async def get_data(self):
        items = []
        list_times = self.app.best_cp_times
        for pcp in list_times:
            items.append({'index': pcp.cp, 'player_nickname': pcp.player.nickname,
                          'record_time': times.format_time(pcp.time), })

        return items









