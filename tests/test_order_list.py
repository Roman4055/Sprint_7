# test_order_list.py
import allure
import pytest
from helpers import get_orders_list
from data import StaticData


@allure.feature("API заказов")
@allure.story("Список заказов: получение и фильтрация")
class TestOrderListPositive:
    """Позитивные тесты: ожидаем статус 200 и валидную структуру ответа."""

    @allure.title("Проверка списка заказов: {allure_name}")
    @allure.description(
        "Проверяем получение списка заказов с разными фильтрами: без фильтров, "
        "по курьеру, постраничная выдача, по ближайшей станции метро. "
        "Ожидаем статус 200, наличие поля 'orders' и корректный тип данных (список)."
    )
    @pytest.mark.parametrize(
        "allure_name, params",
        [
            ("все заказы без фильтров", {}),
            ("заказы конкретного курьера", {"courierId": StaticData.COURIER_ID}),
            ("постраничная выдача: 10 заказов", {"limit": StaticData.LIMIT_PAGE_DEFAULTS}),
            (
                "10 заказов у метро Калужская",
                {**StaticData.LIMIT_PAGE_DEFAULTS, "nearestStation": StaticData.STATION_KALUZHSKAYA},
            ),
        ],
        ids=[
            "all_orders_no_filters",
            "courier_specific_orders",
            "page_limit_default",
            "near_kaluzhskaya",
        ],
    )
    def test_order_list(self, allure_name, params):
        expected_status = 200

        with allure.step("Готовим параметры запроса и фиксируем контекст"):
            allure.attach(
                f"Кейс: {allure_name}\nПараметры запроса: {params}\nОжидаемый статус: {expected_status}",
                name="Контекст теста",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Отправляем GET-запрос на получение списка заказов ({allure_name})"):
            response = get_orders_list(params)

        self._attach_response_details(response)

        with allure.step(f"Проверяем статус-код: ожидаем {expected_status}"):
            assert response.status_code == expected_status, (
                f"Ожидался статус {expected_status}, но получен {response.status_code}. "
                f"Ответ: {response.text[:200]}"
            )

        with allure.step("Проверяем, что ответ — корректный JSON"):
            try:
                order_data = response.json()
            except ValueError as e:
                pytest.fail(f"Не удалось распарсить JSON ответа: {e}. Возможно, сервер вернул битый JSON.")

        with allure.step("Проверяем структуру ответа (поле 'orders' и тип списка)"):
            assert "orders" in order_data, f"В ответе отсутствует поле 'orders'. Ответ: {order_data}"
            assert isinstance(order_data["orders"], list), (
                f"'orders' должен быть списком, а получен {type(order_data['orders']).__name__}."
            )

    def _attach_response_details(self, response):
        allure.attach(
            f"Реальный URL запроса: {response.url}\n"
            f"Status Code: {response.status_code}\n"
            f"Content-Type: {response.headers.get('Content-Type')}\n\n"
            f"Тело ответа:\n{response.text}",
            name="Детали ответа сервера",
            attachment_type=allure.attachment_type.TEXT,
        )


@allure.feature("API заказов")
@allure.story("Список заказов: негативные сценарии")
class TestOrderListNegative404:
    """Негативный тест: заказы несуществующего курьера, ожидаем 404."""

    @allure.title("Негативный тест: заказы несуществующего курьера (ожидается 404)")
    @allure.description(
        "Отправляем запрос на получение списка заказов для несуществующего курьера. "
        "Ожидаем статус 404. При этом в ответе не должно быть валидного списка заказов."
    )
    def test_order_list_nonexistent_courier(self):
        params = {"courierId": StaticData.INCORRECT_ID_COURIER}
        expected_status = 404

        with allure.step("Готовим параметры запроса для несуществующего курьера"):
            allure.attach(
                f"Кейс: заказы несуществующего курьера\nПараметры запроса: {params}\n"
                f"Ожидаемый статус: {expected_status}",
                name="Контекст теста",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Отправляем GET-запрос с несуществующим courierId"):
            response = get_orders_list(params)

        self._attach_response_details(response)

        with allure.step(f"Проверяем статус-код: ожидаем {expected_status}"):
            assert response.status_code == expected_status, (
                f"Ожидался статус {expected_status}, но получен {response.status_code}. "
                f"Ответ: {response.text[:200]}"
            )

        with allure.step("Проверяем, что в ответе на 404 нет валидного списка заказов"):
            try:
                order_data = response.json()
            except ValueError:
                # Битый JSON на 404 — фиксируем как вложение, тест не валим: статус уже проверен выше
                allure.attach(
                    response.text,
                    name="Тело ответа (не JSON)",
                    attachment_type=allure.attachment_type.TEXT,
                )
            else:
                assert "orders" not in order_data, (
                    f"При статусе 404 в ответе неожиданно присутствует поле 'orders': {order_data}"
                )

    def _attach_response_details(self, response):
        allure.attach(
            f"Реальный URL запроса: {response.url}\n"
            f"Status Code: {response.status_code}\n"
            f"Content-Type: {response.headers.get('Content-Type')}\n\n"
            f"Тело ответа:\n{response.text}",
            name="Детали ответа сервера",
            attachment_type=allure.attachment_type.TEXT,
        )
