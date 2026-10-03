import pytest
import requests
from data import Url


def create_courier(payload: dict) -> requests.Response:
    """Отправляет запрос на создание курьера и возвращает ответ."""
    url = f"{Url.MAIN_URL}{Url.API_COURIER_CREATE}"
    return requests.post(url, json=payload)


def login_courier(payload: dict) -> requests.Response:
    """Отправляет запрос на логин курьера и возвращает ответ (в нём есть поле 'id')."""
    url = f"{Url.MAIN_URL}{Url.LOGIN_COURIER}"
    return requests.post(url, json=payload)


def create_and_login_courier(payload: dict) -> str:
    """Создаёт курьера, логинится и возвращает его ID (строкой)."""
    response_create = create_courier(payload)
    assert response_create.status_code == 201, (
        f"Не удалось создать курьера. Статус: {response_create.status_code}. "
        f"Ответ: {response_create.text}")

    login_payload = {"login": payload["login"], "password": payload["password"]}
    response_login = login_courier(login_payload)
    assert response_login.status_code == 200, (
        f"Не удалось залогиниться под созданным курьером. Статус: {response_login.status_code}. "
        f"Ответ: {response_login.text}")

    courier_id = response_login.json().get("id")
    assert courier_id is not None, (
        f"В ответе на логин нет поля 'id'. Ответ: {response_login.text}")
    return str(courier_id)


def delete_courier(courier_id: str) -> requests.Response:
    """Отправляет запрос на удаление курьера по ID. ID передаётся в URL, тело не нужно."""
    url = f"{Url.MAIN_URL}{Url.API_COURIER_DELETE.replace(':id', courier_id)}"
    return requests.delete(url)


def create_order(payload: dict, timeout: int = 10) -> requests.Response:
    """
    Отправляет POST-запрос на создание заказа и возвращает ответ.
    
    :param payload: словарь с данными заказа (firstName, address, color и т.д.)
    :param timeout: таймаут запроса в секундах
    :return: объект ответа requests.Response
    """
    url = f"{Url.MAIN_URL}{Url.ORDERS_LIST}"
    
    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.exceptions.Timeout as e:
        # Пробрасываем ошибку, чтобы pytest её обработал
        pytest.fail(f"Превышен таймаут при создании заказа: {e}")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Ошибка HTTP-запроса при создании заказа: {e}")

    return response

def accept_order(order_id: str, courier_id: str) -> requests.Response:
    """
    Принимает заказ: order_id подставляется в путь, courierId уходит как query-параметр.
    Метод — PUT, как указано в документации.
    """
    url = f"{Url.MAIN_URL}{Url.ACCEPT_ORDER.replace(':id', order_id)}"
    return requests.put(url, params={"courierId": courier_id})


def accept_order_without_order_id(courier_id: str) -> requests.Response:
    """Запрос без номера заказа (в пути нет :id)."""
    url = f"{Url.MAIN_URL}{Url.ACCEPT_ORDER.replace(':id', '')}"
    return requests.put(url, params={"courierId": courier_id})

def get_order_by_track(track: str | None = None) -> requests.Response:
    """
    Получает заказ по трек-номеру.
    track: если None — запрос без параметра t (проверка ошибки).
    Метод GET, параметр t передаётся как query.
    """
    url = f"{Url.MAIN_URL}{Url.TRACK_ORDER}"
    params = {}
    if track is not None:
        params["t"] = track
    return requests.get(url, params=params)