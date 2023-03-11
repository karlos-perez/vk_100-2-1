import typing
from datetime import datetime
from logging import getLogger

from app.game.models import UserModel, STATUS_ERROR
from app.questions.models import QuestionModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


ANSWERS_COUNT = 6


class GameState:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)
        # Simple memory storageЖ
        # Dict active games
        self.active_games: dict[int, int] = {}  # {chat_id: GameModel.id}
        # Dict current question in games
        self.question_games: dict[int, dict] = {}  # {chat_id: dict[QuestionModel]}
        # Dict formatting question adn answers for a beautiful display
        self.format_question_games: dict[int, list[str]] = {}  # {chat_id: list[str]}
        # Dict of users who respond
        self.respondent_users_games: dict[int, int] = {}  # {chat_id: UserModel.id}
        # Dict of current guessed answers in game
        self.guessed_answers_games: dict[int, str] = {}  # {chat_id: list[str]}

    async def restore_state(self):
        # TODO: not optimized
        games = await self.app.store.game.get_active_games()
        for g in games:
            if self.get_active_game(g.chat_id):
                # Close unstopped games due to a crash
                self.logger.info(
                    f"CLOSE GAME: id:{g.id} status: {g.status} "
                    f"date_start: {g.date_begin} date_end: {g.date_end} "
                    f"question_id: {g.question_id}"
                )
                values = {"status": STATUS_ERROR, "date_end": datetime.now()}
                await self.app.store.game.update_game(g.id, values)
            else:
                self.active_games[g.chat_id] = g.id
                self.question_games[g.chat_id] = g.question.to_dict()
                self.format_question_games[g.chat_id] = [g.question.title]
                x = ["XXXXXX"] * ANSWERS_COUNT
                self.format_question_games[g.chat_id].extend(x)
                correct_answers = await self.app.store.game.get_correct_answers(g.id)
                if correct_answers:
                    index = 1
                    unique_answers = [a.answer for a in correct_answers]
                    for a in set(unique_answers):
                        self.set_guessed(g.chat_id, a)
                        self.format_question_games[g.chat_id][index] = a
                        index += 1
                respondent = await self.app.store.game.get_respondent_user(g.id)
                if respondent is not None:
                    self.respondent_users_games[g.chat_id] = respondent.user_id
        self.logger.info(f"active_games: {self.active_games}")
        self.logger.info(f"question_games: {self.question_games}")
        self.logger.info(f"guessed_answers_games: {self.guessed_answers_games}")
        self.logger.info(f"respondent_users_games: {self.respondent_users_games}")
        self.logger.info(f"format_question_games: {self.format_question_games}")

    def get_active_game(self, chat_id: int) -> int | None:
        return self.active_games.get(chat_id)

    def get_respondent_user(self, chat_id: int) -> UserModel.id:
        return self.respondent_users_games.get(chat_id)

    async def set_respondent_user(self, chat_id, user_id):
        game_id = self.get_active_game(chat_id)
        await self.app.store.game.create_participant(user_id, game_id)
        self.respondent_users_games[chat_id] = user_id

    def del_respondent_user(self, chat_id):
        if chat_id in self.respondent_users_games:
            del self.respondent_users_games[chat_id]

    def get_question_in_str(self, chat_id):
        return "<br>".join(self.format_question_games[chat_id])

    def get_answers(self, chat_id: int) -> list[str]:
        return self.question_games[chat_id]["answers"].keys()

    def get_guessed(self, chat_id):
        return self.guessed_answers_games.get(chat_id, [])

    def set_guessed(self, chat_id: int, answer: str):
        if self.guessed_answers_games.get(chat_id) is None:
            self.guessed_answers_games[chat_id] = [answer]
        else:
            self.guessed_answers_games[chat_id].append(answer)

    def get_question_in_str_end(self, chat_id: int) -> str | None:
        guessed_answer = self.get_guessed(chat_id)
        if len(guessed_answer) >= ANSWERS_COUNT:
            return self.get_question_in_str(chat_id)
        else:
            format_answer = self.format_question_games.get(chat_id)
            if not format_answer:  # Not question
                return None
            answers_all = list(self.get_answers(chat_id))
            guessed = self.get_guessed(chat_id)
            if not guessed:  # Not correct answers
                for i in range(1, len(format_answer)):
                    ans = answers_all.pop()
                    score = self.question_games[chat_id]["answers"][ans]
                    format_answer[i] = f"❌ {ans} - {score}"
            not_guessed = set(answers_all) - set(guessed)
            for i in range(1, len(format_answer)):
                if format_answer[i] == "XXXXXX":
                    ans = not_guessed.pop()
                    score = self.question_games[chat_id]["answers"][ans]
                    format_answer[i] = f"❌ {ans} - {score}"
            return "<br>".join(format_answer)

    def set_start_game(self, chat_id: int, game_id: int, question: QuestionModel) -> str:
        self.active_games[chat_id] = game_id
        self.question_games[chat_id] = question.to_dict()
        # Format display question
        self.format_question_games[chat_id] = [question.title]
        x = ["XXXXXX"] * ANSWERS_COUNT
        self.format_question_games[chat_id].extend(x)
        return "<br>".join(self.format_question_games[chat_id])

    async def set_game_over(self, chat_id: int, reason: int):
        game_id = self.get_active_game(chat_id)
        values = {"status": reason, "date_end": datetime.now()}
        await self.app.store.game.update_game(game_id, values)
        # Сlear game data
        if chat_id in self.active_games:
            del self.active_games[chat_id]
        if chat_id in self.question_games:
            del self.question_games[chat_id]
        if chat_id in self.format_question_games:
            del self.format_question_games[chat_id]
        if chat_id in self.respondent_users_games:
            del self.respondent_users_games[chat_id]
        if chat_id in self.guessed_answers_games:
            del self.guessed_answers_games[chat_id]
        return game_id

    def set_correct_answer(self, chat_id: int, answer: str, score: int):
        self.set_guessed(chat_id, answer)
        answer_stat = f"{answer} - {score}"
        index = len(self.guessed_answers_games[chat_id])
        self.format_question_games[chat_id][index] = answer_stat

