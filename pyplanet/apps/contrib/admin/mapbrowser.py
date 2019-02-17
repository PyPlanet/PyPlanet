import logging

from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.contrib.permission import PermissionManager
from pyplanet.contrib.command import CommandManager
from pyplanet.contrib.chat import ChatManager
from pyplanet.contrib.chat.query import ChatQuery
from pyplanet.apps.contrib.admin.views.mapbrowser import BrowserView


class MapBrowser:
    def __init__(self, app):
        self.app = app
        self.instance = app.instance

    async def on_start(self):
        await self.instance.permission_manager.register('localmaps', 'Shows a file browser to browse the local files', app=self.app, min_level=3)

        await self.app.instance.command_manager.register(
            Command(command='localmaps', target=self.show_browser, perms='admin:localmaps', admin=True)
        )

    async def show_browser(self, player, data, **kwargs):
        view = BrowserView(self.app, player)
        await view.set_dir('')
