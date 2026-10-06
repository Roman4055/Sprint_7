# test_accept_order.py
import allure
from api_client import (
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
    def test_accept_order_successfully(self, registered_courier, base_order_payload):
        """Создаём заказ → принимаем заказ курьером из фикстуры → 200 + {'ok': true}."""
        courier_id = registered_courier["courier_id"]

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
        "Особенность: эндпоинт требует обязательного параметра :id в пути; его отсутствие делает запрос семантически некорректным."
    )
    def test_accept_order_without_number(self, registered_courier):
        courier_id = registered_courier["courier_id"]

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
    def test_accept_order_with_nonexistent_number(self, registered_courier):
        courier_id = registered_courier["courier_id"]
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
    def test_accept_order_with_nonexistent_courier(self, base_order_payload):
        with allure.step("Создаём валидный заказ и получаем его трек-номер"):
            response_order = create_order(base_order_payload)
            assert response_order.status_code == Cods.SUCCESSFUL_ORDER, (
                f"Заказ не создан. Статус: {response_order.status_code}. Ответ: {response_order.text}"
            )
            order_number = str(response_order.json()["track"])

        nonexistent_courier = "1000"

        with allure.step(f"Принимаем заказ {order_number} несуществующим курьером {nonexistent_courier}"):
            response = accept_order(order_number, nonexistent_courier)

        with allure.step(f"Проверяем статус-код {Cods.INCORRECT_ID_COURIER}"):
            assert response.status_code == Cods.INCORRECT_ID_COURIER, (
                f"Ожидался статус {Cods.INCORRECT_ID_COURIER}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.INCORRECT_ID_COURIER, (
                f"Ожидалось: '{Messages.INCORRECT_ID_COURIER}', получено: '{actual_message}'"
            )

    @allure.title("Повторное принятие того же заказа другим курьером: ожидается 409")
    @allure.description("Заказ уже в работе — второй курьер не может его принять.")
    def test_accept_order_already_taken(self, courier_factory, base_order_payload):
        courier_1 = courier_factory()
        courier_2 = courier_factory()
        courier_id_1 = courier_1["courier_id"]
        courier_id_2 = courier_2["courier_id"]

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

        with allure.step(f"Первый курьер {courier_id_1} принимает заказ"):
            resp_first = accept_order(order_id, courier_id_1)
            assert resp_first.status_code == Cods.ACCEPT_ORDER, (
                f"Первый курьер не смог принять заказ. Статус: {resp_first.status_code}. "
                f"Ответ: {resp_first.text}"
            )

        with allure.step(f"Второй курьер {courier_id_2} пытается принять уже принятый заказ"):
            response = accept_order(order_id, courier_id_2)

        with allure.step(f"Проверяем статус-код {Cods.OLD_ORDER}"):
            assert response.status_code == Cods.OLD_ORDER, (
                f"Ожидался статус {Cods.OLD_ORDER}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем сообщение о том, что заказ уже в работе"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.OLD_ORDER, (
                f"Ожидалось: '{Messages.OLD_ORDER}', получено: '{actual_message}'"
            )
