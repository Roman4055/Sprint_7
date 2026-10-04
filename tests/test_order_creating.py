# test_order_creating.py
import pytest
import allure
from helpers import create_order
from data import Cods


@allure.feature("Оформление заказа")
@allure.story("Создание заказа с разными вариантами цвета")
class TestOrderCreation:

    @allure.title("Создание заказа: проверка разных вариантов поля color")
    @allure.description(
        "Проверяем, что заказ создаётся с разными вариантами поля color: "
        "один цвет (BLACK), два цвета (BLACK и GREY) и без указания цвета. "
        "Ожидаем статус 201 и непустой track в ответе."
    )
    @pytest.mark.parametrize(
        "color",
        [["BLACK"], ["BLACK", "GREY"], []],
        ids=["one_color_black", "two_colors", "no_color"],
    )
    def test_order_creation(self, color, base_order_payload):
        expected_status = Cods.SUCCESSFUL_ORDER

        with allure.step(f"Готовим payload с цветом {color}"):
            payload = base_order_payload.copy()
            payload["color"] = color  # Подставляем цвет из параметризации

        with allure.step(f"Отправляем запрос на создание заказа (color={color}) через хелпер"):
            response = create_order(payload)

        allure.attach(
            response.text,
            name="Response body",
            attachment_type=allure.attachment_type.JSON,
        )

        with allure.step(f"Проверяем статус-код {expected_status}"):
            assert response.status_code == expected_status, (
                f"Ожидался статус {expected_status}, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        data = response.json()

        with allure.step("Проверяем наличие и непустоту поля 'track'"):
            track = data.get("track")
            assert track, f"Поле 'track' отсутствует или пустое. Ответ: {data}"
