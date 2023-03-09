import typing
from logging import getLogger

from app.game.models import UserModel, STATUS_STOPPED, STATUS_FINISH
from app.store.bot.dataclasses import Message
from app.store.bot.keyboards import Keyboard as kb
from app.store.bot.text import Text

if typing.TYPE_CHECKING:
    from app.web.app import Application


class GameResponse:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)

    async def send_invite_start_game(self, chat_id: int):
        message = Message(peer_id=chat_id, text=Text.invite, buttons=kb.begin_game())
        return await self.app.store.vk_api.send_message(message)

    async def send_invite_start_game_edit(self, chat_id: int, message_id: int):
        message = Message(
            user_id=message_id,
            peer_id=chat_id,
            text=Text.invite
        )
        return await self.app.store.vk_api.send_message_edit(message)

    async def send_game_rules(self, chat_id: int):
        message = Message(
            peer_id=chat_id,
            text=Text.rules,
            buttons=kb.start_button(),
        )
        await self.app.store.vk_api.send_message(message)

    async def send_begin_game(self, chat_id: int, message_id: int):
        message = Message(
            user_id=message_id,
            peer_id=chat_id,
            text=Text.begin,
        )
        await self.app.store.vk_api.send_message_edit(message)

    async def send_question(self, chat_id: int, text: str, button: str = "stop"):
        if button == "answer":
            btn = kb.answer_button()
        elif button == "stop":
            btn = kb.stop_button()
        else:
            btn = kb.empty()
        message = Message(peer_id=chat_id, text=text, buttons=btn)
        await self.app.store.vk_api.send_message(message)

    async def edit_question(self, chat_id: int, message_id: int, text: str):
        message = Message(
            user_id=message_id, peer_id=chat_id, text=text, buttons=kb.empty()
        )
        await self.app.store.vk_api.send_message_edit(message)

    async def send_end_game(
        self, user: UserModel, peer_id: int, reason: int, stat: list[tuple[int, str]]
    ):
        if len(stat) == 1:
            winner = f"{stat[0][1]} - {stat[0][0]}"
            game_stat = Text.end_stat_one.format(winner=winner)
        elif len(stat) > 1:
            users_points = "<br>".join([f"{i[1]} - {i[0]}" for i in stat])
            winner = f"{stat[0][1]} - {stat[0][0]}"
            game_stat = Text.end_stat.format(winner=winner, gamers=users_points)
        else:
            game_stat = ""
        if reason == STATUS_STOPPED:
            text = f"{Text.end_stopped.format(user=user.fullname)}" f"{game_stat}"
        elif reason == STATUS_FINISH:
            text = f"{Text.end_finish}{game_stat}"
        else:
            text = Text.error_status
        message = Message(
            user_id=user.id, peer_id=peer_id, text=text, buttons=kb.empty()
        )
        await self.app.store.vk_api.send_message(message)

    async def send_respondent_user(self, chat_id: int, fullname: str):
        text = Text.respondent_user.format(fullname=fullname)
        message = Message(peer_id=chat_id, text=text, buttons=kb.stop_button())
        await self.app.store.vk_api.send_message(message)

    async def send_answer_correct(self, chat_id: int, user_name: str, score: int):
        text = Text.right_answer.format(fullname=user_name, score=score)
        message = Message(peer_id=chat_id, text=text, buttons=kb.stop_button())
        await self.app.store.vk_api.send_message(message)

    async def send_answer_incorrect(self, chat_id: int, attempts: int):
        text = Text.incorrect_answer.format(attempts=attempts)
        message = Message(peer_id=chat_id, text=text, buttons=kb.stop_button())
        await self.app.store.vk_api.send_message(message)

    async def send_user_lose(
        self, chat_id: int, fullname: str, score: int, attempts: int
    ):
        text = Text.user_lose.format(fullname=fullname, attempts=attempts, score=score)
        message = Message(peer_id=chat_id, text=text, buttons=kb.stop_button())
        await self.app.store.vk_api.send_message(message)

    async def send_snackbar(self, user_id: int, chat_id: int, event_id: str):
        event_data = {"type": "show_snackbar", "text": Text.user_lose_snackbar}
        message = Message(user_id=user_id, peer_id=chat_id, text=event_id)
        await self.app.store.vk_api.send_event_answer(message, event_data)
