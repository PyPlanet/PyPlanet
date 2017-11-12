from pyplanet.views.generics.widget import WidgetView


class ClockWidget(WidgetView):
    widget_x = 150
    widget_y = -59
    template_name = 'clock/clock.xml'

    def __init__(self, app):
        super().__init__(self)
        self.app = app
        self.manager = app.context.ui
        self.id = 'pyplanet__widgets_clock'
