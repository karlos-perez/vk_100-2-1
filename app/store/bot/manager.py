import typing
from dataclasses import dataclass
from logging import getLogger

from app.store.vk_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


# Time given for a response in seconds
ANSWER_TIME = 60


@dataclass
class EventType:
    new: str = f"message_new"
    event: str = f"message_event"
    reply: str = f"message_reply"
    invite: str = f"chat_invite_user_by_link"


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)

        self._conversation_message_id = {}
        self.respondent_user_games: dict[int:int] = {}  # {chat_id: UserModel.id}
        self.guessed_answers_games: dict[
            int : list[str]
        ] = {}  # {chat_id: ['str', 'str']}
        self.format_question_games: dict[int : list[str]] = {}
        self.losing_users_game: dict[
            int : list[int]
        ] = {}  # {chat_id: [user_id, user_id]}

    async def handler_updates(self, updates: list[Update]):
        for update in updates:
            if update.type == EventType.new:
                await self.app.store.game_manager.handler_message_new(update.object)
            elif update.type == EventType.event:
                await self.app.store.game_manager.handler_message_event(update.object)
            elif update.type == EventType.reply:
                pass
