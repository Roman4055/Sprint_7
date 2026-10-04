# test_login_courier.py

import allure
from helpers import login_courier
from data import Cods, Messages


@allure.feature("API курьеров")
@allure.story("Логин курьера")
class TestLoginCourier:
    """Тесты ручки логина курьера: POST /api/v1/courier/login."""

    @allure.title("Курьер может авторизоваться с корректными данными, в ответе есть id")
    @allure.description(
        "Сценарий: курьер создан фикстурой → логинимся с корректными данными → "
        "проверяем статус 200 и наличие положительного числового id."
    )
    def test_login_successfully(self, registered_courier):
        payload = registered_courier["payload"].copy()

        with allure.step("Отправляем POST-запрос на логин курьера через хелпер"):
            response = login_courier(payload)

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
    @allure.description("Отправляем запрос без поля login — ожидаем 400 'Недостаточно данных для входа'.")
    def test_login_without_login(self, registered_courier):
        payload = registered_courier["payload"].copy()
        del payload["login"]

        with allure.step("Отправляем запрос без поля login"):
            response = login_courier(payload)

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
    @allure.description("Отправляем запрос с пустой строкой в поле login — ожидаем 400 'Недостаточно данных для входа'.")
    def test_login_with_empty_login(self, registered_courier):
        payload = registered_courier["payload"].copy()
        payload["login"] = ""

        with allure.step("Отправляем запрос с пустой строкой в поле login"):
            response = login_courier(payload)

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
    @allure.description(
        "Согласно документации ожидалось 400 'Недостаточно данных для входа'.\n"
        "Если тест падает с 504 — это баг на бэкенде: не хватает защиты/валидации."
    )
    def test_login_without_password(self, registered_courier):
        payload = registered_courier["payload"].copy()
        del payload["password"]

        with allure.step("Отправляем запрос без поля password"):
            # Теперь timeout корректно обрабатывается хелпером
            response = login_courier(payload, timeout=30)

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
    @allure.description("Отправляем запрос с пустой строкой в поле password — ожидаем 400 'Недостаточно данных для входа'.")
    def test_login_with_empty_password(self, registered_courier):
        payload = registered_courier["payload"].copy()
        payload["password"] = ""

        with allure.step("Отправляем запрос с пустой строкой в поле password"):
            response = login_courier(payload)

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
    @allure.description("Отправляем запрос с изменённым паролем — ожидаем 404 с сообщением об ошибке авторизации.")
    def test_login_with_wrong_password(self, registered_courier):
        payload = registered_courier["payload"].copy()
        payload["password"] = payload["password"] + "_wrong"

        with allure.step("Отправляем запрос с неверным паролем"):
            response = login_courier(payload)

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
    @allure.description("Курьер специально не создаётся — проверяем логин по несуществующим данным: ожидаем 404.")
    def test_login_nonexistent_courier(self, random_courier_payload):
        payload = random_courier_payload.copy()

        with allure.step("Отправляем запрос с данными курьера, которого нет в системе"):
            response = login_courier(payload)

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
