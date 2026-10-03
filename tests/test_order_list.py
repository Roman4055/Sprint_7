# test_order_list.py
import allure
import pytest
import requests
from data import Url, StaticData

# Позитивные кейсы: (название для отчёта, параметры запроса, ожидаемый статус)
ORDER_LIST_CASES = [
    ("все заказы без фильтров", {}, 200),
    ("заказы конкретного курьера", {"courierId": StaticData.COURIER_ID}, 200),
    ("постраничная выдача: 10 заказов", StaticData.LIMIT_PAGE_DEFAULTS, 200),
    (
        "10 заказов у метро Калужская",
        {**StaticData.LIMIT_PAGE_DEFAULTS, "nearestStation": StaticData.STATION_KALUZHSKAYA},
        200,
    ),
]


class TestOrderListPositive:
    """Позитивные тесты: ожидаем статус 200 и валидную структуру ответа."""

    @allure.title("Проверка списка заказов: {case_name}")
    @pytest.mark.parametrize(
        "case_name, params, expected_status",
        ORDER_LIST_CASES,
        ids=[case[0] for case in ORDER_LIST_CASES],
    )
    def test_order_list(self, case_name, params, expected_status):
        base_url = f"{Url.MAIN_URL}{Url.ORDERS_LIST}"

        with allure.step("Контекст: подготовка запроса и баг документации"):
            allure.attach(
                f"""
                Кейс: {case_name}
                Параметры запроса: {params}
                Ожидаемый статус: {expected_status}

                ⚠️ БАГ ДОКУМЕНТАЦИИ: в документации указан неверный путь
                /v1/orders?courierId=... — без префикса /api/.

                Запрос по пути из документации возвращает HTML-страницу
                или 405 Not Allowed.

                ✅ В тесте используется исправленный путь: {base_url}
                (с префиксом /api/) — он корректно возвращает JSON.
                """,
                name="Контекст теста и баг документации",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Отправляем GET-запрос к {base_url}"):
            response = requests.get(base_url, params=params, timeout=60)


        self._attach_response_details(response)

        with allure.step(f"Проверяем статус-код: ожидаем {expected_status}"):
            assert response.status_code == expected_status, (
                f"Ожидался статус {expected_status}, но получен {response.status_code}. "
                f"Ответ: {response.text[:200]}"
            )

        with allure.step("Проверяем, что ответ — JSON"):
            try:
                order_data = response.json()
            except ValueError as e:
                pytest.fail(f"Не удалось распарсить JSON ответа: {e}. Возможно, сервер вернул битый JSON.")

        with allure.step("Проверяем структуру ответа (поле 'orders' и тип списка)"):
            assert "orders" in order_data, f"В ответе отсутствует поле 'orders'. Ответ: {order_data}"
            assert isinstance(order_data["orders"], list), (
                f"'orders' должен быть списком, а получен {type(order_data['orders']).__name__}."
            )

    @allure.title("Заказы курьера на станциях Бульвар Рокоссовского и Черкизовская (BUG BACKEND)")
    def test_order_list_stations_bug(self):
        base_url = f"{Url.MAIN_URL}{Url.ORDERS_LIST}"
        params = {
            "courierId": StaticData.COURIER_ID,
            "nearestStation": StaticData.STATIONS_ROKOSOVSKOGO_CHERKIZOVSKAYA,
        }
        expected_status = 200

        with allure.step("Контекст: подготовка запроса, баг документации и известный баг бэкенда"):
            allure.attach(
                f"""
                Кейс: заказы курьера на станциях Бульвар Рокоссовского и Черкизовская
                Параметры запроса: {params}
                Ожидаемый статус: {expected_status}

                ⚠️ БАГ ДОКУМЕНТАЦИИ: в документации указан неверный путь
                /v1/orders?courierId=... — без префикса /api/.
                Запрос по пути из документации возвращает HTML-страницу
                или 405 Not Allowed.

                ✅ В тесте используется исправленный путь: {base_url}.

                🐛 ИЗВЕСТНЫЙ БАГ БЭКЕНДА: при передаче нескольких nearestStation
                сервер возвращает 500 с ошибкой парсинга JSON
                (Unexpected token , in JSON at position 1).
                Поведение подтверждено в Postman. Тест падает по контракту
                (ожидаем 200) и фиксирует баг бэкенда.
                """,
                name="Контекст теста: баг документации и баг бэкенда",
                attachment_type=allure.attachment_type.TEXT,
            )


        with allure.step(f"Отправляем GET-запрос к {base_url}"):
            response = requests.get(base_url, params=params, timeout=60)

        self._attach_response_details(response)

        # До ассерта фиксируем диагностику: если сервер упал с 500 — это баг бэкенда
        if response.status_code == 500:
            with allure.step("BUG BACKEND: сервер вернул 500 на валидный запрос"):
                allure.attach(
                    f"""
                    Статус: 500
                    Ответ: {response.text}

                    Запрос сформирован корректно (множественные query-параметры nearestStation).
                    Такое же поведение подтверждено в Postman.
                    Вывод: баг бэкенда, а НЕ ошибка автотеста.
                    Тест падает ожидаемо — баг нужно завести в трекер.
                    """,
                    name="Анализ ошибки 500: BUG BACKEND",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with allure.step(f"Проверяем статус-код: ожидаем {expected_status}"):
            assert response.status_code == expected_status, (
                f"Ожидался статус {expected_status}, но получен {response.status_code}. "
                f"Ответ: {response.text[:200]}"
            )

        with allure.step("Проверяем, что ответ — JSON и содержит поле 'orders'"):
            try:
                order_data = response.json()
            except ValueError as e:
                pytest.fail(f"Не удалось распарсить JSON ответа: {e}. Сервер вернул битый JSON.")

            assert "orders" in order_data, f"В ответе отсутствует поле 'orders'. Ответ: {order_data}"
            assert isinstance(order_data["orders"], list), (
                f"'orders' должен быть списком, а получен {type(order_data['orders']).__name__}."
            )

    @staticmethod
    def _attach_response_details(response):
        allure.attach(
            f"Реальный URL запроса: {response.url}\n"
            f"Status Code: {response.status_code}\n"
            f"Content-Type: {response.headers.get('Content-Type')}\n\n"
            f"Тело ответа:\n{response.text}",
            name="Детали ответа сервера",
            attachment_type=allure.attachment_type.TEXT,
        )


class TestOrderListNegative404:
    """Негативный тест: запрашиваем заказы несуществующего курьера, ожидаем 404."""

    @allure.title("Негативный тест: заказы несуществующего курьера (ожидается 404)")
    def test_order_list_nonexistent_courier(self):
        base_url = f"{Url.MAIN_URL}{Url.ORDERS_LIST}"
        params = {"courierId": StaticData.INCORRECT_ID_COURIER}
        expected_status = 404

        with allure.step("Контекст: подготовка запроса"):
            allure.attach(
                f"Кейс: заказы несуществующего курьера\nПараметры запроса: {params}\n"
                f"Ожидаемый статус: {expected_status} (по документации)",
                name="Контекст теста",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Отправляем GET-запрос к {base_url}"):
            response = requests.get(base_url, params=params, timeout=60)

        TestOrderListPositive._attach_response_details(response)

        with allure.step(f"Проверяем статус-код: ожидаем {expected_status}"):
            assert response.status_code == expected_status, (
                f"Ожидался статус {expected_status}, но получен {response.status_code}. "
                f"Ответ: {response.text[:200]}"
            )

        # Для 404 допустимо отсутствие JSON, но если он есть — проверяем, что это не список заказов
        try:
            order_data = response.json()
            if "orders" in order_data:
                pytest.warn(
                    f"При статусе 404 в ответе неожиданно присутствует поле 'orders': {order_data}"
                )
        except ValueError:
            pass
