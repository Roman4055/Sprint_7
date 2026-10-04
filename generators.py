# generators.py
import random
import string


def generate_random_string(length: int) -> str:
    """Генерирует случайную строку из строчных латинских букв."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def get_random_courier_payload() -> dict:
    """Возвращает случайные данные для регистрации курьера."""
    return {
        "login": generate_random_string(10),
        "password": generate_random_string(10),
        "firstName": generate_random_string(10),
    }
