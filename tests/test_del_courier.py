# test_del_courier.py

import allure
import requests
from helpers import create_and_login_courier, delete_courier
from data import Url, Messages, Cods


@allure.feature("API курьеров")
@allure.story("Удаление курьера")
class TestDeleteCourier:

    @allure.title("Успешное удаление курьера: статус 200 и ok: true")
    def test_delete_existing_courier(self, random_courier_payload):
        """Сценарий: создаём курьера, логинимся -> получаем ID -> удаляем -> проверяем 200 и {'ok': true}."""
        payload = random_courier_payload.copy()

        with allure.step("Создаём курьера и логинимся, получаем его ID"):
            courier_id = create_and_login_courier(payload)

        with allure.step(f"Отправляем DELETE-запрос на удаление курьера с ID={courier_id}"):
            response_delete = delete_courier(courier_id)

        with allure.step(f"Проверяем статус-код {Cods.SUCCESSFUL_DEL}"):
            assert response_delete.status_code == Cods.SUCCESSFUL_DEL, (
                f"Ожидался статус {Cods.SUCCESSFUL_DEL}, но получен {response_delete.status_code}. "
                f"Ответ: {response_delete.text}"
            )

        with allure.step("Проверяем, что в ответе поле 'ok' равно True"):
            assert response_delete.json().get("ok") is True, (
                f"Поле 'ok' не равно True. Ответ: {response_delete.json()}"
            )

    @allure.title("Запрос без ID: ожидается ошибка 400 и сообщение о недостатке данных.")
    @allure.description("По документации ожидалось 400 'message':  'Недостаточно данных для удаления курьера'")
    def test_delete_without_id(self):
        """Сценарий: DELETE на ручку без ID в пути -> 400 + сообщение об ошибке."""
        url = f"{Url.MAIN_URL}{Url.API_COURIER_DELETE.replace(':id', '')}"

        with allure.step(f"Отправляем DELETE-запрос без ID на {url}"):
            response = requests.delete(url)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_ID_DEL}"):
            assert response.status_code == Cods.MISSING_ID_DEL, (
                f"Ожидался статус {Cods.MISSING_ID_DEL}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MISSING_ID_DEL, (
                f"Сообщение об ошибке не соответствует ожидаемому. "
                f"Ожидалось: '{Messages.MISSING_ID_DEL}', получено: '{actual_message}'"
            )

    @allure.title("Запрос с несуществующим ID: ожидается ошибка 404 и сообщение о ненайденном курьере.")
    @allure.description(
    "Баг: в фактическом ответе сервера сообщение 'Курьера с таким id нет.' "
    "содержит точку, которой нет в документации. Тест падает — это фиксация бага.")
    def test_delete_nonexistent_courier(self):
        """Сценарий: DELETE с несуществующим ID -> 404 + сообщение об ошибке."""
        nonexistent_id = "999999999"

        with allure.step(f"Отправляем DELETE-запрос для несуществующего курьера (ID={nonexistent_id})"):
            response = delete_courier(nonexistent_id)

        with allure.step(f"Проверяем статус-код {Cods.INCORRECT_ID_DEL}"):
            assert response.status_code == Cods.INCORRECT_ID_DEL, (
                f"Ожидался статус {Cods.INCORRECT_ID_DEL}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.INCORRECT_ID_DEL, (
                f"Сообщение об ошибке не соответствует ожидаемому. "
                f"Ожидалось: '{Messages.INCORRECT_ID_DEL}', получено: '{actual_message}'"
            )
