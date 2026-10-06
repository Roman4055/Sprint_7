# test_get_order_by_number.py

import allure
from api_client import create_order, get_order_by_track
from data import Cods, Messages


@allure.feature("API заказов")
@allure.story("Получение заказа по трек-номеру")
class TestGetOrderByTrack:

    @allure.title("Успешный запрос: возвращается заказ с track=X")
    @allure.description(
        "Сценарий: создаём заказ → получаем его по track → "
        "проверяем статус 200 и совпадение track."
    )
    def test_get_order_successfully(self, base_order_payload):
        with allure.step("Создаём заказ и получаем его трек-номер"):
            response_create = create_order(base_order_payload)
            assert response_create.status_code == Cods.SUCCESSFUL_ORDER, (
                f"Заказ не создан. Статус: {response_create.status_code}. Ответ: {response_create.text}"
            )
            created_order = response_create.json()
            track_number = created_order.get("track")
            assert track_number is not None, "В ответе создания заказа нет поля track"

        with allure.step(f"Получаем заказ по трек-номеру {track_number}"):
            response = get_order_by_track(track_number)

        with allure.step(f"Проверяем статус-код {Cods.SUCCESSFUL_TRACK}"):
            assert response.status_code == Cods.SUCCESSFUL_TRACK, (
                f"Ожидался статус {Cods.SUCCESSFUL_TRACK}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем, что в ответе есть объект order и трек совпадает"):
            data = response.json()
            order = data.get("order")
            assert order is not None, f"В ответе нет объекта order. Ответ: {data}"
            assert order.get("track") == track_number, (
                f"Трек в ответе ({order.get('track')}) не совпадает с запрошенным ({track_number})"
            )

    @allure.title("Запрос без трек-номера: ожидается 400")
    @allure.description("Если не передать параметр t, сервер должен вернуть ошибку 'Недостаточно данных для поиска'.")
    def test_get_order_missing_track(self):
        with allure.step("Отправляем запрос без параметра t"):
            response = get_order_by_track(None)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_TRACK}"):
            assert response.status_code == Cods.MISSING_TRACK, (
                f"Ожидался статус {Cods.MISSING_TRACK}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MISSING_TRACK, (
                f"Ожидалось: '{Messages.MISSING_TRACK}', получено: '{actual_message}'"
            )

    @allure.title("Запрос с несуществующим трек-номером: ожидается 404")
    @allure.description("При запросе несуществующего трека сервер должен вернуть 404 и сообщение 'Заказ не найден'.")
    def test_get_order_nonexistent_track(self):
        with allure.step("Готовим несуществующий трек-номер"):
            nonexistent_track = "999999999"

        with allure.step(f"Отправляем запрос с несуществующим треком {nonexistent_track}"):
            response = get_order_by_track(nonexistent_track)

        with allure.step(f"Проверяем статус-код {Cods.INCORRECT_TRACK}"):
            assert response.status_code == Cods.INCORRECT_TRACK, (
                f"Ожидался статус {Cods.INCORRECT_TRACK}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.INCORRECT_TRACK, (
                f"Ожидалось: '{Messages.INCORRECT_TRACK}', получено: '{actual_message}'"
            )
