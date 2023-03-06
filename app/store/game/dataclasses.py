from dataclasses import dataclass, field


@dataclass
class BotCommand:
    start: str = "/start"
    stop: str = "/stop"
    status: str = "/status"  # For the futureOn


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
