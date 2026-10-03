# Проверь:
# успешный запрос возвращает{"ok":true};
# если не передать id курьера, запрос вернёт ошибку;
# если передать неверный id курьера, запрос вернёт ошибку;
# если не передать id заказа, запрос вернёт ошибку;
# если передать неверный id заказа, запрос вернёт ошибку.

# test_accept_order.py

import allure
from helpers import (
    create_and_login_courier,
    get_order_by_track,
    create_order,
    accept_order,
    accept_order_without_order_id,
)
from data import Cods, Messages


@allure.feature("API заказов")
@allure.story("Принятие заказа")
class TestAcceptOrder:

    @allure.title("Успешное принятие заказа: статус 200 и ok: true")
    def test_accept_order_successfully(self, random_courier_payload, base_order_payload):
        """Создаём курьера и заказ → принимаем заказ этим курьером → 200 + {'ok': true}."""
        payload = random_courier_payload.copy()

        with allure.step("Создаём курьера и получаем его ID"):
            courier_id = create_and_login_courier(payload)

        with allure.step("Создаём заказ и получаем его трек-номер"):
            response_order = create_order(base_order_payload)
            assert response_order.status_code == Cods.SUCCESSFUL_ORDER, (
                f"Заказ не создан. Статус: {response_order.status_code}. Ответ: {response_order.text}"
            )
            track_number = str(response_order.json()["track"])

        with allure.step(f"Получаем заказ по треку {track_number} и достаём его внутренний ID"):
            response_by_track = get_order_by_track(track_number)
            assert response_by_track.status_code == Cods.SUCCESSFUL_TRACK, (
                f"Не удалось получить заказ по треку. Статус: {response_by_track.status_code}. "
                f"Ответ: {response_by_track.text}"
            )
            order_id = str(response_by_track.json()["order"]["id"])

        with allure.step(f"Принимаем заказ (id={order_id}, track={track_number}) курьером {courier_id}"):
            response = accept_order(order_id, courier_id)

        with allure.step(f"Проверяем статус-код {Cods.ACCEPT_ORDER}"):
            assert response.status_code == Cods.ACCEPT_ORDER, (
                f"Ожидался статус {Cods.ACCEPT_ORDER}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем, что в ответе поле 'ok' равно True"):
            assert response.json().get("ok") is True, (
                f"Поле 'ok' не равно True. Ответ: {response.json()}"
            )

    @allure.title("Запрос без номера заказа: ожидается ошибка 400")
    @allure.description(
    "Сценарий проверяет обработку отсутствующего идентификатора заказа в URL-пути.\n"
    "Ожидаемое поведение: API возвращает 400 Bad Request с сообщением об ошибке.\n"
    "Особенность: эндпоинт требует обязательного параметра :id в пути; его отсутствие делает запрос семантически некорректным.\n"
    "В документации есть вариант ручки 'Запрос без номера', я не совсем понял тут моя ошибка или нет ")
    def test_accept_order_without_number(self, random_courier_payload):
        courier_id = create_and_login_courier(random_courier_payload)

        with allure.step("Отправляем запрос без номера заказа в пути"):
            response = accept_order_without_order_id(courier_id)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_NUM}"):
            assert response.status_code == Cods.MISSING_NUM, (
                f"Ожидался статус {Cods.MISSING_NUM}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MISSING_NUM, (
                f"Ожидалось: '{Messages.MISSING_NUM}', получено: '{actual_message}'"
            )

    @allure.title("Запрос с несуществующим номером заказа: ожидается 404")
    @allure.description("Проверяем обработку несуществующего номера заказа.")
    def test_accept_order_with_nonexistent_number(self, random_courier_payload):
        courier_id = create_and_login_courier(random_courier_payload)
        nonexistent_order = "999999999"

        with allure.step(f"Принимаем несуществующий заказ {nonexistent_order}"):
            response = accept_order(nonexistent_order, courier_id)

        with allure.step(f"Проверяем статус-код {Cods.INCORRECT_NUM}"):
            assert response.status_code == Cods.INCORRECT_NUM, (
                f"Ожидался статус {Cods.INCORRECT_NUM}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.INCORRECT_NUM, (
                f"Ожидалось: '{Messages.INCORRECT_NUM}', получено: '{actual_message}'"
            )

    @allure.title("Запрос с несуществующим ID курьера: ожидается 404")
    @allure.description("Проверяем обработку несуществующего ID курьера.")
    def test_accept_order_with_nonexistent_courier(self):
        # Создаём валидный заказ
        response_order = create_order(
            {
                "firstName": "Naruto",
                "lastName": "Uchiha",
                "address": "Konoha, 142 apt.",
                "metroStation": 4,
                "phone": "+7 800 355 35 35",
                "rentTime": 5,
                "deliveryDate": "2026-06-06",
                "comment": "Saske, come back to Konoha",
            }
        )
        assert response_order.status_code == Cods.SUCCESSFUL_ORDER
        order_number = str(response_order.json()["track"])

        nonexistent_courier = "1000"  # из StaticData.INCORRECT_ID_COURIER

        with allure.step(f"Принимаем заказ {order_number} несуществующим курьером {nonexistent_courier}"):
            response = accept_order(order_number, nonexistent_courier)

        with allure.step(f"Проверяем статус-код {Cods.INCORRECT_ID_COURIER}"):
            assert response.status_code == Cods.INCORRECT_ID_COURIER, (
                f"Ожидался статус {Cods.INCORRECT_ID_COURIER}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            # В документации для несуществующего курьера указано: 'Курьера с таким id не существует'
            # Если в Messages.INCORRECT_ID_COURIER у тебя другая фраза — поправь сравнение.
            assert actual_message == Messages.INCORRECT_ID_COURIER, (
                f"Ожидалось: '{Messages.INCORRECT_ID_COURIER}', получено: '{actual_message}'"
            )

    @allure.title("Повторное принятие того же заказа другим курьером: ожидается 409")
    @allure.description("Заказ уже в работе — второй курьер не может его принять.")
    def test_accept_order_already_taken(self, random_courier_payload):
        payload_1 = random_courier_payload.copy()
        payload_2 = random_courier_payload.copy()
        # Чтобы логины не совпали, можно добавить суффикс, если фикстура не гарантирует уникальность
        payload_2["login"] = payload_2["login"] + "_2"
        payload_2["password"] = payload_2["password"] + "_2"

        # Курьер 1
        courier_id_1 = create_and_login_courier(payload_1)

        # Создаём заказ
        response_order = create_order(
            {
                "firstName": "Naruto",
                "lastName": "Uchiha",
                "address": "Konoha, 142 apt.",
                "metroStation": 4,
                "phone": "+7 800 355 35 35",
                "rentTime": 5,
                "deliveryDate": "2026-06-06",
                "comment": "Saske, come back to Konoha",
            }
        )
        assert response_order.status_code == Cods.SUCCESSFUL_ORDER
        order_number = str(response_order.json()["track"])

        # Первый курьер принимает заказ
        resp_first = accept_order(order_number, courier_id_1)
        assert resp_first.status_code == Cods.ACCEPT_ORDER

        # Второй курьер пытается принять тот же заказ
        courier_id_2 = create_and_login_courier(payload_2)

        with allure.step(f"Второй курьер {courier_id_2} пытается принять уже принятый заказ {order_number}"):
            response = accept_order(order_number, courier_id_2)

        with allure.step(f"Проверяем статус-код {Cods.OLD_ORDER} (Conflict)"):
            assert response.status_code == Cods.OLD_ORDER, (
                f"Ожидался статус {Cods.OLD_ORDER}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем сообщение о том, что заказ уже в работе"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.OLD_ORDER, (
                f"Ожидалось: '{Messages.OLD_ORDER}', получено: '{actual_message}'"
            )
