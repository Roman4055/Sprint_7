# test_creating_courier.py
import allure
from helpers import create_courier, login_courier, delete_courier
from data import Cods, Messages


class TestCreatingCourier:
    """Тесты ручки создания курьера: POST /api/v1/courier."""

    @allure.title("Курьера можно создать при передаче обязательных полей")
    def test_create_courier_successfully(self, random_courier_payload):
        payload = random_courier_payload.copy()

        with allure.step("Создаём курьера с корректными данными"):
            response = create_courier(payload)

        with allure.step("Проверяем статус-код 201"):
            assert response.status_code == 201, (
                f"Ожидался статус 201, но получен {response.status_code}. Ответ: {response.text}"
            )

        with allure.step("Проверяем, что в ответе 'ok' равно True"):
            assert response.json().get("ok") is True, (
                f"Поле 'ok' не равно True. Ответ: {response.json()}"
            )

        with allure.step("Удаляем созданного курьера"):
            login_response = login_courier({"login": payload["login"], "password": payload["password"]})
            courier_id = login_response.json().get("id")
            if courier_id:
                delete_courier(str(courier_id))

    @allure.title("Нельзя создать двух курьеров с одинаковым логином")
    @allure.description("В данном случае етсть Баг в документации.\n"
                        "По документации ожидался ответ 'Этот логин уже используется'")
    def test_create_courier_with_duplicate_login(self, random_courier_payload):
        payload = random_courier_payload.copy()

        with allure.step("Создаём первого курьера"):
            response_first = create_courier(payload)
            assert response_first.status_code == 201, (
                f"Ожидался статус 201, но получен {response_first.status_code}. Ответ: {response_first.text}"
            )

        with allure.step("Пытаемся создать второго курьера с тем же логином"):
            response_second = create_courier(payload)

        with allure.step("Проверяем статус-код 409"):
            assert response_second.status_code == 409, (
                f"Ожидался статус 409, но получен {response_second.status_code}. Ответ: {response_second.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response_second.json().get("message", "")
            assert actual_message == Messages.MESSAGE_DOUBLE_COURIER, (
                f"Ожидалось: '{Messages.MESSAGE_DOUBLE_COURIER}', получено: '{actual_message}'"
            )

        with allure.step("Удаляем созданного курьера"):
            login_response = login_courier({"login": payload["login"], "password": payload["password"]})
            courier_id = login_response.json().get("id")
            if courier_id:
                delete_courier(str(courier_id))

    @allure.title("Нельзя создать курьера без логина")
    def test_create_courier_without_login(self, random_courier_payload):
        payload = random_courier_payload.copy()
        del payload["login"]

        with allure.step("Отправляем запрос без поля login"):
            response = create_courier(payload)

        with allure.step("Проверяем статус-код 400"):
            assert response.status_code == 400, (
                f"Ожидался статус 400, но получен {response.status_code}. Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MESSAGE_NOT_ENOUGH_DATA, (
                f"Ожидалось: '{Messages.MESSAGE_NOT_ENOUGH_DATA}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя создать курьера с пустой строкой в логине")
    def test_create_courier_with_empty_login(self, random_courier_payload):
        payload = random_courier_payload.copy()
        payload["login"] = ""

        with allure.step("Отправляем запрос с пустой строкой в поле login"):
            response = create_courier(payload)

        with allure.step("Проверяем статус-код 400"):
            assert response.status_code == 400, (
                f"Ожидался статус 400, но получен {response.status_code}. Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MESSAGE_NOT_ENOUGH_DATA, (
                f"Ожидалось: '{Messages.MESSAGE_NOT_ENOUGH_DATA}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя создать курьера без пароля")
    def test_create_courier_without_password(self, random_courier_payload):
        payload = random_courier_payload.copy()
        del payload["password"]

        with allure.step("Отправляем запрос без поля password"):
            response = create_courier(payload)

        with allure.step("Проверяем статус-код 400"):
            assert response.status_code == 400, (
                f"Ожидался статус 400, но получен {response.status_code}. Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MESSAGE_NOT_ENOUGH_DATA, (
                f"Ожидалось: '{Messages.MESSAGE_NOT_ENOUGH_DATA}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя создать курьера с пустой строкой в пароле")
    def test_create_courier_with_empty_password(self, random_courier_payload):
        payload = random_courier_payload.copy()
        payload["password"] = ""

        with allure.step("Отправляем запрос с пустой строкой в поле password"):
            response = create_courier(payload)

        with allure.step("Проверяем статус-код 400"):
            assert response.status_code == 400, (
                f"Ожидался статус 400, но получен {response.status_code}. Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MESSAGE_NOT_ENOUGH_DATA, (
                f"Ожидалось: '{Messages.MESSAGE_NOT_ENOUGH_DATA}', получено: '{actual_message}'"
            )
