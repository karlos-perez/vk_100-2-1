import json
import typing

from app.store.bot.dataclasses import BotAction


class VkKeyboard:
    def __init__(self, one_time=False, inline=False):
        self.one_time = one_time
        self.inline = inline
        self.lines = [[]]
        self.keyboard = {
            "one_time": self.one_time,
            "inline": self.inline,
            "buttons": self.lines,
        }

    def get_keyboard(self):
        return json.dumps(self.keyboard)

    @classmethod
    def get_empty_keyboard(cls):
        keyboard = cls()
        keyboard.keyboard["buttons"] = []
        keyboard.keyboard["one_time"] = True
        return keyboard.get_keyboard()

    def add_button(
        self, label: str, color: str = "secondary", payload: dict | None = None
    ):
        if payload is not None and not isinstance(payload, str):
            payload = json.dumps(payload)
        button_type = "text"
        current_line = self.lines[-1]
        current_line.append(
            {
                "color": color,
                "action": {
                    "type": button_type,
                    "payload": payload,
                    "label": label,
                },
            }
        )

    def add_callback_button(
        self, label: str, color: str = "secondary", payload: typing.Any = None
    ):
        current_line = self.lines[-1]
        if payload is not None and not isinstance(payload, str):
            payload = json.dumps(payload)

        button_type = "callback"

        current_line.append(
            {
                "color": color,
                "action": {
                    "type": button_type,
                    "payload": payload,
                    "label": label,
                },
            }
        )


class Keyboard:
    @staticmethod
    def empty():
        # Create clear/empty buttons
        button_empty = VkKeyboard(inline=True)
        return button_empty.get_empty_keyboard()

    @staticmethod
    def begin_game():
        # Create invite game buttons
        button_start_game = VkKeyboard(inline=True)
        button_start_game.add_callback_button(
            "Правила", "primary", payload={"type": BotAction.rules_game}
        )
        button_start_game.add_callback_button(
            "Старт", "positive", payload={"type": BotAction.start_game}
        )
        return button_start_game.get_keyboard()

    @staticmethod
    def start_button():
        # Create Start button
        button_start = VkKeyboard(inline=True)
        button_start.add_callback_button(
            "Старт", "positive", payload={"type": BotAction.start_game}
        )
        return button_start.get_keyboard()

    @staticmethod
    def stop_button():
        # Create Stop game button
        button_stop = VkKeyboard(one_time=True)
        button_stop.add_callback_button(
            "Остановить игру", "negative", payload={"type": BotAction.stop_game}
        )
        return button_stop.get_keyboard()

    @staticmethod
    def answer_button():
        # Create Answer button
        button_answer = VkKeyboard(inline=True)
        button_answer.add_callback_button(
            "Ответить", "primary", payload={"type": BotAction.touch_answer}
        )
        return button_answer.get_keyboard()
