import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.admin.accessor import AdminAccessor
        from app.store.queue.accessor import QueueAccessor
        from app.store.questions.accessor import QuestionAccessor
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.game.accessor import GameAccessor
        from app.store.bot.manager import BotManager

        self.admins = AdminAccessor(app)
        self.vk_api = VkApiAccessor(app)
        if app.config.queue.enable:
            self.queue = QueueAccessor(app)
        self.questions = QuestionAccessor(app)
        self.game = GameAccessor(app)
        self.bot_manager = BotManager(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
