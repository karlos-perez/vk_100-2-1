from dataclasses import dataclass


@dataclass
class Text:
    invite: str = (
        f"Привет.<br>"
        f"Я - бот для игры в<br>"
        f"1️⃣0️⃣0️⃣ к 1️⃣<br>"
        f"Я знаю команды:<br>"
        f" /start - начать новую игру.<br>"
        f" /stop - завершить игру.<br>"
        f"Приятной игры.<br>"
        f"Чтобы начать игру жми 👇"
    )
    rules: str = (
        f"📖 Правила игры.<br>"
        f"Объявляется вопрос. Необходимо угадать все шесть ответов. "
        f"Каждый ответ имеет своё количество баллов.<br>"
        f'Игрок, который раньше остальных нажимает на кнопку "Ответить"'
        f" – получает возможность написать ответ на вопрос. "
        f"Если Игрок угадал один из шести ответов, то ему начисляются "
        f"соответствующие количество баллов. И даётся возможность "
        f"написать еще ответ. В случае трёх неправильных ответов - "
        f"игрок выбывает.<br>"
        f"Игра продолжается до тех пора, пока:<br>"
        f"1. Не будут отгаданы все варианты ответов.<br>"
        f"2. Один из пользователей не закончит ее нажав "
        f'на кнопку "Закончить игру" или отправит /stop<br>'
        f"3. Все игроки выбывают.<br>"
        f"Приятной игры.<br>"
        f"Чтобы начать игру жми 👇"
    )
    begin: str = f"П О Е Х А Л И !!!<br>" \
                 f"Вопрос:"
    end_stat_one: str = (
        "Победитель 🏆 и единственный участник:<br>" "🥇 {winner}<br>" "<br>"
    )
    end_stat: str = (
        "Победитель 🏆:<br>"
        "🥇 {winner}<br>"
        "<br>"
        "Остальные участники:<br>"
        "{gamers}"
    )
    end_stopped: str = (
        "Игра завершена<br>" "Пользователь:<br>{user}<br>остановил игру<br>" "<br>"
    )
    end_finish: str = "Игра завершена<br>Поздравляю Вы прошли игру 🎉<br><br>"
    error_status: str = "Произошла какая-то ошибка"
    respondent_user: str = "Отвечает пользователь:<br>{fullname}"
    right_answer: str = "Это правильный ответ  ✅<br>" "{fullname} %2B{score}"
    incorrect_answer: str = (
        "Нет такого ответа ❌<br>Кол-во попыток: {attempts}<br><br>Попробуйте ещё..."
    )
    user_lose: str = (
        "Нет такого ответа ❌<br>"
        "Пользователь:<br>"
        "{fullname}<br>"
        "Выбывает из игры<br>"
        "Кол-во попыток: {attempts}<br>"
        "Кол-во баллов: {score}"
    )
    user_lose_snackbar: str = f"Вы не можете больше отвечать"
