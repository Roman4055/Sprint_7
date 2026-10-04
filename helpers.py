# helpers.py
import allure
import requests
from data import Url


@allure.step("Отправляем POST-запрос на создание курьера")
def create_courier(payload: dict) -> requests.Response:
    """Отправляет запрос на создание курьера и возвращает ответ."""
    url = f"{Url.MAIN_URL}{Url.API_COURIER_CREATE}"
    return requests.post(url, json=payload)


@allure.step("Отправляем POST-запрос на логин курьера")
def login_courier(payload: dict, timeout: int = 60) -> requests.Response:
    """Отправляет запрос на логин курьера и возвращает ответ."""
    url = f"{Url.MAIN_URL}{Url.LOGIN_COURIER}"
    return requests.post(url, json=payload, timeout=timeout)


@allure.step("Отправляем DELETE-запрос на удаление курьера")
def delete_courier(courier_id: str) -> requests.Response:
    """Отправляет запрос на удаление курьера по ID. ID передаётся в URL, тело не нужно."""
    url = f"{Url.MAIN_URL}{Url.API_COURIER_DELETE.replace(':id', courier_id)}"
    return requests.delete(url)


@allure.step("Отправляем POST-запрос на создание заказа")
def create_order(payload: dict, timeout: int = 10) -> requests.Response:
    """Отправляет POST-запрос на создание заказа и возвращает ответ."""
    url = f"{Url.MAIN_URL}{Url.ORDERS_LIST}"
    return requests.post(url, json=payload, timeout=timeout)


@allure.step("Отправляем PUT-запрос на принятие заказа")
def accept_order(order_id: str, courier_id: str) -> requests.Response:
    """Принимает заказ: order_id подставляется в путь, courierId уходит как query-параметр."""
    url = f"{Url.MAIN_URL}{Url.ACCEPT_ORDER.replace(':id', order_id)}"
    return requests.put(url, params={"courierId": courier_id})


@allure.step("Отправляем PUT-запрос на принятие заказа без номера заказа")
def accept_order_without_order_id(courier_id: str) -> requests.Response:
    """Запрос без номера заказа (в пути нет :id)."""
    url = f"{Url.MAIN_URL}{Url.ACCEPT_ORDER.replace(':id', '')}"
    return requests.put(url, params={"courierId": courier_id})


@allure.step("Отправляем GET-запрос на получение заказа по трек-номеру")
def get_order_by_track(track_number) -> requests.Response:
    """Получает заказ по трек-номеру. Если track_number None — параметр не передаётся."""
    url = f"{Url.MAIN_URL}{Url.ORDERS_LIST}"
    params = {}
    if track_number is not None:
        params["track"] = track_number
    return requests.get(url, params=params)


@allure.step("Отправляем GET-запрос на получение списка заказов")
def get_orders_list(params: dict = None, timeout: int = 60) -> requests.Response:
    """Получает список заказов. Фильтры передаются как query-параметры."""
    url = f"{Url.MAIN_URL}{Url.ORDERS_LIST}"
    return requests.get(url, params=params, timeout=timeout)
