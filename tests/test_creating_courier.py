# test_creating_courier.py
import allure
from helpers import create_courier, login_courier
from data import Cods, Messages


@allure.feature("API курьеров")
@allure.story("Создание курьера")
class TestCreatingCourier:
    """Тесты ручки создания курьера: POST /api/v1/courier."""

    @allure.title("Курьера можно создать при передаче обязательных полей")
    def test_create_courier_successfully(self, registered_courier):
        """Проверяем успешное создание курьера. Создание и удаление — в фикстуре."""
        payload = registered_courier["payload"]
        courier_id = registered_courier["courier_id"]

        with allure.step("Проверяем, что курьер создан и ID получен"):
            assert courier_id, "ID курьера не получен"

        with allure.step("Логинимся под созданным курьером и подтверждаем его существование"):
            login_response = login_courier({"login": payload["login"], "password": payload["password"]})
            assert login_response.status_code == Cods.SUCCESSFUL_LOGIN, (
                f"Не удалось залогиниться. Статус: {login_response.status_code}. "
                f"Ответ: {login_response.text}"
            )
            response_id = login_response.json().get("id")
            assert str(response_id) == courier_id, (
                f"ID из логина ({response_id}) не совпадает с ID из фикстуры ({courier_id})"
            )

    @allure.title("Нельзя создать двух курьеров с одинаковым логином")
    @allure.description(
        "В данном случае есть баг в документации.\n"
        "По документации ожидался ответ 'Этот логин уже используется'"
    )
    def test_create_courier_with_duplicate_login(self, registered_courier, random_courier_payload):
        """Первый курьер создаётся фикстурой, второй — с тем же логином, ожидаем 409."""
        first_payload = registered_courier["payload"]

        with allure.step(f"Пытаемся создать второго курьера с тем же логином '{first_payload['login']}'"):
            second_payload = random_courier_payload.copy()
            second_payload["login"] = first_payload["login"]
            second_payload["password"] = first_payload["password"]
            response_second = create_courier(second_payload)

        with allure.step(f"Проверяем статус-код {Cods.DOUBLE_COURIER}"):
            assert response_second.status_code == Cods.DOUBLE_COURIER, (
                f"Ожидался статус {Cods.DOUBLE_COURIER}, но получен {response_second.status_code}. "
                f"Ответ: {response_second.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response_second.json().get("message", "")
            assert actual_message == Messages.MESSAGE_DOUBLE_COURIER, (
                f"Ожидалось: '{Messages.MESSAGE_DOUBLE_COURIER}', получено: '{actual_message}'"
            )

    @allure.title("Нельзя создать курьера без логина")
    def test_create_courier_without_login(self, random_courier_payload):
        payload = random_courier_payload.copy()
        del payload["login"]

        with allure.step("Отправляем запрос без поля login"):
            response = create_courier(payload)

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
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

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
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

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
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

        with allure.step(f"Проверяем статус-код {Cods.MISSING_LOGIN_PASSWORD}"):
            assert response.status_code == Cods.MISSING_LOGIN_PASSWORD, (
                f"Ожидался статус {Cods.MISSING_LOGIN_PASSWORD}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Проверяем текст сообщения об ошибке"):
            actual_message = response.json().get("message", "")
            assert actual_message == Messages.MESSAGE_NOT_ENOUGH_DATA, (
                f"Ожидалось: '{Messages.MESSAGE_NOT_ENOUGH_DATA}', получено: '{actual_message}'"
            )
