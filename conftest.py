import pytest
import allure
from generators import get_random_courier_payload
from api_client import create_courier, login_courier, delete_courier


@pytest.fixture
def random_courier_payload():
    """Случайные данные для регистрации курьера."""
    return get_random_courier_payload()


@pytest.fixture
def registered_courier():
    """Создаёт и логинит курьера до теста, удаляет после — независимо от результата теста."""
    payload = get_random_courier_payload()

    with allure.step("Фикстура: создаём курьера"):
        create_courier(payload)


    with allure.step("Фикстура: логинимся и получаем ID курьера"):
        response_login = login_courier({"login": payload["login"], "password": payload["password"]})
        courier_id = response_login.json().get("id")

    yield {"payload": payload, "courier_id": str(courier_id)}

    with allure.step(f"Фикстура: удаляем курьера с ID={courier_id}"):
        delete_courier(str(courier_id))


@pytest.fixture
def courier_factory():
    """Фабрика курьеров: создаёт курьеров по запросу теста, удаляет всех созданных после."""
    created = []

    def _make_courier():
        payload = get_random_courier_payload()
        create_courier(payload)

        response_login = login_courier({"login": payload["login"], "password": payload["password"]})
        courier_id = response_login.json().get("id")

        courier = {"payload": payload, "courier_id": str(courier_id)}
        created.append(courier)
        return courier

    yield _make_courier

    for courier in created:
        delete_courier(courier["courier_id"])


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
        "comment": "Saske, come back to Konoha",
    }
