# # test_login_courier.py
import allure
import requests
from data import Url, Cods, Messages


class TestLoginCourier:
    """Тесты ручки логина курьера: POST /api/v1/courier/login."""

    def login(self, payload: dict):
        """Отправляет запрос на логин с таймаутом 60 секунд."""
        return requests.post(f"{Url.MAIN_URL}{Url.LOGIN_COURIER}", json=payload, timeout=60)

    @allure.title("Курьер может авторизоваться с корректными данными, в ответе есть id")
    def test_login_successfully(self, registered_courier):
        payload = registered_courier["payload"].copy()

        with allure.step("Отправляем POST-запрос на логин курьера"):
            response = self.login(payload)

        with allure.step(f"Проверяем статус-код {Cods.SUCCESSFUL_LOGIN}"):
            assert response.status_code == Cods.SUCCESSFUL_LOGIN, (
                f"Ожидался статус {Cods.SUCCESSFUL_LOGIN}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем, что в ответе получен id курьера"):
            courier_data = response.json()
            assert "id" in courier_data, f"В ответе отсутствует поле 'id'. Ответ: {courier_data}"
            assert isinstance(courier_data["id"], int), (
                f"'id' должен быть целым числом, получено: {courier_data['id']!r}"
            )
            assert courier_data["id"] > 0, f"'id' должен быть положительным числом"

    @allure.title("Нельзя авторизоваться без поля логина")
    def test_login_without_login(self, registered_courier):
        payload = registered_courier["payload"].copy()
        del payload["login"]

        with allure.step("Отправляем запрос без поля login"):
            response = self.login(payload)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MISSING_LOGIN_PASSWORD, (
                f"Ожидалось: '{Messages.MISSING_LOGIN_PASSWORD}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя авторизоваться с пустой строкой в логине")
    def test_login_with_empty_login(self, registered_courier):
        payload = registered_courier["payload"].copy()
        payload["login"] = ""

        with allure.step("Отправляем запрос с пустой строкой в поле login"):
            response = self.login(payload)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MISSING_LOGIN_PASSWORD, (
                f"Ожидалось: '{Messages.MISSING_LOGIN_PASSWORD}', получено: '{actual_message}'"
            )
    @allure.title("Тест попытки авторизоваться без поля пароля")
    @allure.description("Согласно документации ожидалось 400 'Недостаточно данных для входа'\n"
                         "Тест падает с 504, вероятно не хватает какой-то защиты на бекенде")
    def test_login_without_password(self, registered_courier):
        payload = registered_courier["payload"].copy()
        del payload["password"]

        with allure.step("Отправляем запрос без поля password"):
            response = self.login(payload, timeout=30)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MISSING_LOGIN_PASSWORD, (
                f"Ожидалось: '{Messages.MISSING_LOGIN_PASSWORD}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя авторизоваться с пустой строкой в пароле")
    def test_login_with_empty_password(self, registered_courier):
        payload = registered_courier["payload"].copy()
        payload["password"] = ""

        with allure.step("Отправляем запрос с пустой строкой в поле password"):
            response = self.login(payload)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MISSING_LOGIN_PASSWORD, (
                f"Ожидалось: '{Messages.MISSING_LOGIN_PASSWORD}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя авторизоваться с неверным паролем")
    def test_login_with_wrong_password(self, registered_courier):
        payload = registered_courier["payload"].copy()
        payload["password"] = payload["password"] + "_wrong"

        with allure.step("Отправляем запрос с неверным паролем"):
            response = self.login(payload)

        with allure.step(f"Проверяем статус-код {Cods.INCORRECT_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.INCORRECT_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.INCORRECT_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.INCORRECT_LOGIN_PASSWORD, (
                f"Ожидалось: '{Messages.INCORRECT_LOGIN_PASSWORD}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя авторизоваться под несуществующим курьером")
    def test_login_nonexistent_courier(self, random_courier_payload):
        # Курьер специально не создаётся — проверяем логин по несуществующим данным.
        payload = random_courier_payload.copy()

        with allure.step("Отправляем запрос с данными курьера, которого нет в системе"):
            response = self.login(payload)

        with allure.step(f"Проверяем статус-код {Cods.INCORRECT_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.INCORRECT_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.INCORRECT_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.INCORRECT_LOGIN_PASSWORD, (
                f"Ожидалось: '{Messages.INCORRECT_LOGIN_PASSWORD}', получено: '{actual_message}'"
            )
