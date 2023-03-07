from dataclasses import dataclass, field, astuple


@dataclass
class EventType:
    new: str = f"message_new"
    event: str = f"message_event"
    reply: str = f"message_reply"
    invite: str = f"chat_invite_user_by_link"


@dataclass
class BotCommand:
    start: str = "/start"
    stop: str = "/stop"
    status: str = "/status"  # For the futureOn

    def is_command(self, text: str) -> bool:
        if text in astuple(self):
            return True
        return False


@dataclass
class BotAction:
    """For button callback"""

    start_game: str = "start_new_game"
    stop_game: str = "stop_game"
    rules_game: str = "game_rules"
    touch_answer: str = "touch_answer_button"


@dataclass
class Message:
    peer_id: int
    text: str
    user_id: int | None = None
    buttons: list = field(default_factory=list)
