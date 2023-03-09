import asyncio
import typing
from datetime import datetime
from logging import getLogger

from app.game.models import STATUS_STOPPED, STATUS_ERROR, STATUS_FINISH
from app.store.bot.dataclasses import EventType, BotCommand, BotAction
from app.store.bot.response import GameResponse
from app.store.game.state import GameState
from app.store.utils import is_message_from_chat
from app.store.vk_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


ANSWERS_COUNT = 6

STAGE_WAIT_PRESS_ANSWER_BUTTON = 1
STAGE_WAIT_ANSWER_FROM_USER = 2


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)
        self.response = GameResponse(app)
        self.state = None
        app.on_startup.append(self.connect)
        # Last bot message
        self.conversation_message_id: dict[int, int] = {}  # {chat_id: id_message}
        # Dict stage in game
        self.stage_game: dict[int, int] = {}  # {chat_id: STAGE}

    async def connect(self, *args, **kwargs):
        self.state = GameState(self.app)
        # Restore last sate games
        self.logger.info(f"Recovery state game:")
        await self.state.restore_state()
        await self.recovery_game()

    async def recovery_game(self):
        games = self.state.active_games.keys()
        for chat_id in games:
            if self.is_waiting_button_press(chat_id):
                # Active game and waiting pressing button "Answer"
                self.stage_game[chat_id] = STAGE_WAIT_PRESS_ANSWER_BUTTON
                question_str = self.state.get_question_in_str(chat_id)
                await self.response.send_question(chat_id, question_str, "answer")
            else:
                # Active game and waiting answer user
                self.stage_game[chat_id] = STAGE_WAIT_ANSWER_FROM_USER
                user_id = self.state.get_respondent_user(chat_id)
                user = await self.app.store.game.get_user_by_id(user_id)
                await self.response.send_respondent_user(chat_id, user.fullname)
            self.logger.info(f"STAGE GAME in chat: {chat_id} - "
                             f"{self.stage_game.get(chat_id)}")

    def set_conversation_message(self, chat_id: int, id_: int | None):
        if id_ is not None:
            self.conversation_message_id[chat_id] = id_

    async def received_bot_command(self, user_id: int, chat_id: int, text: str):
        active_game = self.state.get_active_game(chat_id)
        if text == BotCommand.start:
            if active_game is None:
                await self.response.send_invite_start_game(chat_id)
        elif text == BotCommand.stop:
            if active_game:
                await self.game_action_stop(user_id, chat_id, STATUS_STOPPED)
        else:
            pass

    async def handler_updates(self, updates: list[Update]):
        for update in updates:
            if update.type == EventType.new:
                message = update.object.get("message")
                await self.handler_message_new(message)
            elif update.type == EventType.event:
                await self.handler_message_event(update.object)
            elif update.type == EventType.reply:
                pass

    async def handler_message_new(self, data: dict):
        chat_id = data["peer_id"]

        if is_message_from_chat(chat_id):
            user_id = data["from_id"]
            text = data["text"].strip().lower()
            await self.app.store.game.get_or_create_user(user_id)
            self.set_conversation_message(chat_id, data.get("conversation_message_id"))

            if BotCommand().is_command(text):
                await self.received_bot_command(user_id, chat_id, text)
                return

            if self.state.get_active_game(chat_id) is not None:
                if self.stage_game.get(chat_id) == STAGE_WAIT_ANSWER_FROM_USER:
                    try:
                        await self.game_action_user_answer(user_id, chat_id, text)
                    except Exception as err:
                        self.logger.exception(err)
                        await self.state.set_game_over(chat_id, STATUS_ERROR)
                # TODO: Does not delete messages admin
                else:  # Wait touch button and delete new_message
                    await self.app.store.vk_api.send_message_delete(
                        self.conversation_message_id[chat_id],
                        chat_id,
                    )

    async def handler_message_event(self, data: dict):
        chat_id = data["peer_id"]
        user_id = data["user_id"]
        type_event = data["payload"].get("type")
        self.set_conversation_message(chat_id, data.get("conversation_message_id"))
        await self.app.store.game.get_or_create_user(user_id)

        # View rulers
        if type_event == BotAction.rules_game:
            await self.game_action_rules(chat_id)
        # Start game
        elif type_event == BotAction.start_game:
            if self.state.get_active_game(chat_id) is None:
                await self.game_action_start(chat_id)
        # Touch Answer
        elif type_event == BotAction.touch_answer:
            await self.game_action_touch_answer(user_id, chat_id, data["event_id"])
        # Stop game
        elif type_event == BotAction.stop_game:
            await self.game_action_stop(user_id, chat_id, STATUS_STOPPED)

    async def game_action_rules(self, chat_id: int):
        await self.response.send_invite_start_game_edit(
            chat_id,
            self.conversation_message_id.get(chat_id)
        )
        await self.response.send_game_rules(chat_id)

    async def game_action_start(self, chat_id: int):
        await self.response.send_begin_game(
            chat_id, self.conversation_message_id.get(chat_id)
        )
        question = await self.app.store.questions.get_random_questions()
        game = await self.app.store.game.create_game(
            chat_id=chat_id, date=datetime.now(), question_id=question.id
        )
        format_question = self.state.set_start_game(chat_id, game.id, question)
        await asyncio.sleep(1)  # frequency restrictions
        await self.response.send_question(chat_id, format_question, "answer")

    async def game_action_stop(self, user_id: int, chat_id: int, reason: int):
        final_question = self.state.get_question_in_str_end(chat_id)
        game_id = await self.state.set_game_over(chat_id, reason)
        users_statistic = await self.app.store.game.get_user_game_points(game_id)
        user_who_stopped = await self.app.store.game.get_user_by_id(user_id)
        stat = [(u.score, u.user.fullname) for u in users_statistic]
        await self.response.send_end_game(user_who_stopped, chat_id, reason, stat)
        await asyncio.sleep(1)  # frequency restrictions

        if final_question is not None:
            await self.response.send_question(chat_id, final_question, "empty")
            await asyncio.sleep(1)
        await self.response.send_invite_start_game(chat_id)

    async def game_action_touch_answer(self, user_id: int, chat_id: int, event_id: str):
        # permission = await self.state.can_user_respond(user_id, chat_id)
        if not await self.can_user_respond(user_id, chat_id):
            # Send snackbar user - he loser
            await self.response.send_snackbar(user_id, chat_id, event_id)
            return
        await self.state.set_respondent_user(chat_id, user_id)
        question_str = self.state.get_question_in_str(chat_id)
        # Edit last message: repeat question and delete button "Answer"
        await self.response.edit_question(
            chat_id, self.conversation_message_id[chat_id], question_str
        )
        user = await self.app.store.game.get_user_by_id(user_id)
        await asyncio.sleep(1)  # frequency restrictions
        # Send who answer and added stop button
        await self.response.send_respondent_user(chat_id, user.fullname)
        self.stage_game[chat_id] = STAGE_WAIT_ANSWER_FROM_USER

    async def game_action_user_answer(self, user_id: int, chat_id: int, text: str):
        respondent_id = self.state.get_respondent_user(chat_id)

        # Check who sent the answer
        if respondent_id is None or user_id != respondent_id:
            # TODO: Does not delete admin messages
            await self.app.store.vk_api.send_message_delete(
                self.conversation_message_id[chat_id],
                chat_id,
            )
            return
        answer = text.strip().lower()
        game_id = self.state.get_active_game(chat_id)
        participant = await self.app.store.game.get_participant_by_user_id(
            user_id, game_id
        )
        await self.app.store.game.create_answer_game(
            participant.id, game_id, answer, True
        )

        if self.is_correct_answer(chat_id, answer):
            score_answer = self.state.question_games[chat_id]["answers"][answer]
            score_user = participant.score + score_answer
            await self.app.store.game.update_participant(
                participant.id, {"score": score_user}
            )
            self.state.set_correct_answer(chat_id, answer, score_answer)

            await self.response.send_answer_correct(chat_id,
                                                    participant.user.fullname,
                                                    score_answer)
            await asyncio.sleep(1)  # frequency restrictions

            if self.is_game_over(chat_id):
                await self.game_action_stop(user_id, chat_id, STATUS_FINISH)
            else:
                question_str = self.state.get_question_in_str(chat_id)
                await self.response.send_question(chat_id, question_str, "stop")
                await asyncio.sleep(1)  # frequency restrictions
                # Checking game over
                await self.response.send_respondent_user(chat_id,
                                                         participant.user.fullname)
        else:
            attempts = participant.attempts - 1
            await self.app.store.game.update_participant(
                participant.id, {"attempts": attempts}
            )

            if self.is_user_lose(attempts):
                self.state.del_respondent_user(chat_id)

                await self.response.send_user_lose(
                    chat_id,
                    participant.user.fullname,
                    participant.score,
                    attempts
                )
                await asyncio.sleep(1)  # frequency restrictions
                await self.response.send_question(
                    chat_id, self.state.get_question_in_str(chat_id), "answer"
                )
                self.stage_game[chat_id] = STAGE_WAIT_PRESS_ANSWER_BUTTON
            else:
                await self.response.send_answer_incorrect(chat_id, attempts)

    def is_waiting_button_press(self, chat_id: int) -> bool:
        if self.state.get_respondent_user(chat_id) is None:
            return True
        return False

    def is_correct_answer(self, chat_id: int, text: str) -> bool:
        answers = self.state.get_answers(chat_id)
        guessed = self.state.get_guessed(chat_id)
        if text in answers and text not in guessed:
            return True
        return False

    def is_game_over(self, chat_id: int) -> bool:
        if len(self.state.get_guessed(chat_id)) >= ANSWERS_COUNT:
            return True
        return False

    def is_user_lose(self, attempts) -> bool:
        if attempts <= 0:
            return True
        return False

    async def can_user_respond(self, user_id, chat_id):
        game_id = self.state.get_active_game(chat_id)
        user = await self.app.store.game.get_participant_by_user_id(user_id, game_id)
        if user:
            return False
        return True
