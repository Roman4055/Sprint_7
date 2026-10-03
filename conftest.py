#conftest.py
import random
import string
import pytest
from data import StaticData
from helpers import create_and_login_courier, delete_courier

def generate_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


@pytest.fixture
def random_courier_payload():
    """Случайные данные для регистрации курьера."""
    return {
        "login": generate_random_string(10),
        "password": generate_random_string(10),
        "firstName": generate_random_string(10),
    }


@pytest.fixture
def registered_courier():
    """Создаёт курьера до теста и удаляет его после — независимо от результата теста."""
    payload = {
        "login": generate_random_string(10),
        "password": generate_random_string(10),
        "firstName": generate_random_string(10),
    }
    courier_id = create_and_login_courier(payload)

    yield {"payload": payload, "courier_id": courier_id}

    delete_courier(courier_id)


# Метод возвращающий логин и пароль статичного пользователя для тестов логина
@pytest.fixture
def get_log_pas():
    
    payload = {
        "login": StaticData.LOGIN,
        "password": StaticData.PASSWORD,
    }

    return payload

@pytest.fixture
def base_order_payload():
    """Базовый payload для создания заказа (с фиксированными данными для стабильности)."""
    return {
        "firstName": "Naruto",
        "lastName": "Uchiha",
        "address": "Konoha, 142 apt.",
        "metroStation": 4,
        "phone": "+7 800 355 35 35",
        "rentTime": 5,
        "deliveryDate": "2026-06-06",
        "comment": "Saske, come back to Konoha",}