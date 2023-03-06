import asyncio
import typing
from logging import getLogger

from app.game.models import STATUS_STOPPED, STATUS_FINISH, STATUS_ERROR
from app.store.game.dataclasses import BotAction, BotCommand

from app.store.game.response import GameResponse
from app.store.game.state import GameState

if typing.TYPE_CHECKING:
    from app.web.app import Application


STAGE_WAIT_PRESS_ANSWER_BUTTON = 1
STAGE_WAIT_ANSWER_FROM_USER = 2


class GameManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)
        self.response = GameResponse(app)
        self.state = None
        self.stage = None  # Game stage
        # Last bot message
        self.conversation_message_id: dict[int:int] = {}  # {chat_id: id_message}
        app.on_startup.append(self.connect)
        self.stage_game: dict[int:int] = {}  # {chat_id: STAGE}

    async def connect(self, *args, **kwargs):
        self.state = GameState(self.app)
        # Restore last sate games
        self.logger.info(f"Recovery state game:")
        await self.state.restore_state()
        await self.recovery_game()

    async def recovery_game(self):
        games = self.state.active_games.keys()
        for chat_id in games:
            if self.state.get_respondent_user(chat_id) is None:
                # Active game and waiting pressing button "Answer"
                self.stage = STAGE_WAIT_PRESS_ANSWER_BUTTON
                question_str = self.state.get_question_in_str(chat_id)
                await self.response.send_question(chat_id, question_str, "answer")
            else:
                # Active game and waiting answer user
                self.stage = STAGE_WAIT_ANSWER_FROM_USER
                user_id = self.state.get_respondent_user(chat_id)
                user = await self.app.store.game.get_user_by_id(user_id)
                await self.response.send_respondent_user(chat_id, user.fullname)
            self.logger.info(f"STAGE GAME in chat: {chat_id} - {self.stage}")

    async def handler_message_new(self, data: dict):
        chat_id = data["message"]["peer_id"]
        user_id = data["message"]["from_id"]
        await self.state.get_or_create_user(user_id)
        text = data["message"]["text"].strip().lower()
        if data["message"].get("conversation_message_id"):
            self.conversation_message_id[chat_id] = data["message"].get("conversation_message_id")
        # Сhecking that the message came from the chat
        if chat_id > 2000000000:
            if self.state.get_active_game(chat_id) is None:
                if (
                    text == BotCommand.start
                ):  # Not active game in chat and command START - let's play
                    await self.response.send_invite_start_game(chat_id)
            else:  # Active game and user sent a message
                if text == BotCommand.stop:  # command STOP
                    await self.game_action_stop(user_id, chat_id, STATUS_STOPPED)
                else:
                    if self.stage == STAGE_WAIT_ANSWER_FROM_USER:
                        try:
                            await self.game_action_user_answer(user_id, chat_id, text)
                        except Exception as err:
                            self.logger.exception(exc_info=err)
                            await self.state.close_game(chat_id, STATUS_ERROR)
                    # TODO: Does not delete messages
                    else:  # Wait touch button and delete new_message
                        await self.app.store.vk_api.send_message_delete(
                            self.conversation_message_id[chat_id],
                            chat_id,
                        )
        else:  # TODO: if the user sent a message in a personal
            pass

    async def handler_message_event(self, data: dict):
        chat_id = data["peer_id"]
        user_id = data["user_id"]
        await self.state.get_or_create_user(user_id)
        type_event = data["payload"].get("type")
        if data.get("conversation_message_id"):
            self.conversation_message_id[chat_id] = data.get("conversation_message_id")
        # View rulers
        if type_event == BotAction.rules_game:
            await self.response.send_game_rules(
                chat_id
            )
        # Start game
        elif type_event == BotAction.start_game:
            await self.game_action_start(user_id, chat_id)
        # Touch Answer
        elif type_event == BotAction.touch_answer:
            await self.game_action_touch_answer(user_id, chat_id, data["event_id"])
        # Stop game
        elif type_event == BotAction.stop_game:
            await self.game_action_stop(user_id, chat_id, STATUS_STOPPED)

    async def game_action_start(self, user_id: int, chat_id: int):
        await self.response.send_begin_game(
            chat_id, self.conversation_message_id.get(chat_id, 0)
        )
        format_question = await self.state.start_game(chat_id)
        await asyncio.sleep(1)  # frequency restrictions
        await self.response.send_question(chat_id, format_question, "answer")

    async def game_action_stop(self, user_id: int, chat_id: int, reason: int):
        final_question = self.state.get_question_in_str_end(chat_id)
        game_id = await self.state.close_game(chat_id, reason)
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
        permission = await self.state.can_user_respond(user_id, chat_id)
        if not permission:
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
        self.stage = STAGE_WAIT_ANSWER_FROM_USER

    async def game_action_user_answer(self, user_id: int, chat_id: int, text: str):
        respondent_id = self.state.get_respondent_user(chat_id)
        # Check who sent the answer
        if respondent_id is None or user_id != respondent_id:
            # TODO: Does not delete messages
            await self.app.store.vk_api.send_message_delete(
                self.conversation_message_id[chat_id],
                chat_id,
            )
            # Ignore this message
            return
        answer = text.strip().lower()
        answers = self.state.get_answers(chat_id)
        guessed = self.state.get_guessed(chat_id)
        # Сheck if the answer is correct
        if answer in answers:
            # Checking for the repetition of an answer
            if answer in guessed:
                (
                    fullname,
                    score,
                    attempts,
                ) = await self.state.incorrect_answer_on_question(
                    respondent_id, chat_id, answer
                )
                # Checking the user has more attempts
                if attempts > 0:
                    await self.response.send_answer_incorrect(chat_id, attempts)
                else:  # User lose the game
                    self.state.del_respondent_user(chat_id)
                    await self.response.send_user_lose(
                        chat_id, fullname, score, attempts
                    )
                    await asyncio.sleep(1)  # frequency restrictions
                    await self.response.send_question(
                        chat_id, self.state.get_question_in_str(chat_id), "answer"
                    )
                    self.stage = STAGE_WAIT_PRESS_ANSWER_BUTTON
            else:  # Right answer
                stat = await self.state.correct_answer_on_question(
                    user_id, chat_id, answer
                )
                await self.response.send_answer_correct(chat_id, stat)
                await asyncio.sleep(1)  # frequency restrictions
                # Resend question with right answer
                question_str = self.state.get_question_in_str(chat_id)
                await self.response.send_question(chat_id, question_str, "stop")
                await asyncio.sleep(1)  # frequency restrictions
                # Checking game over
                if len(self.state.get_guessed(chat_id)) >= 6:  # Finish game
                    await self.game_action_stop(user_id, chat_id, STATUS_FINISH)
                else:
                    await self.response.send_respondent_user(chat_id, stat[0])
        else:  # Incorrect answer
            fullname, score, attempts = await self.state.incorrect_answer_on_question(
                user_id, chat_id, answer
            )
            # Checking the user has more attempts
            if attempts > 0:
                await self.response.send_answer_incorrect(chat_id, attempts)
            else:  # User lose the game
                self.state.del_respondent_user(chat_id)
                await self.response.send_user_lose(chat_id, fullname, score, attempts)
                await asyncio.sleep(1)  # frequency restrictions
                await self.response.send_question(
                    chat_id, self.state.get_question_in_str(chat_id), "answer"
                )
                self.stage = STAGE_WAIT_PRESS_ANSWER_BUTTON
