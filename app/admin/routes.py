import typing

from app.admin.views import (
    AdminCurrentView,
    AdminStatisticView,
    AdminStatisticGameView,
    AdminStatisticUserView,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.admin.views import AdminLoginView

    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)
    app.router.add_view("/admin.statistic", AdminStatisticView)
    app.router.add_view("/admin.statistic.games", AdminStatisticGameView)
    app.router.add_view("/admin.statistic.users", AdminStatisticUserView)
