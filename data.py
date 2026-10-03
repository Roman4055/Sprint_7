# data.py

class Url:
    MAIN_URL = 'https://qa-scooter.praktikum-services.ru' # Основной URL

    API_COURIER_CREATE = "/api/v1/courier"          # для POST
    API_COURIER_DELETE = "/api/v1/courier/:id"      # для DELETE

    LOGIN_COURIER = '/api/v1/courier/login'# Ручка Логина курьера
    ORDERS_LIST = '/api/v1/orders' # Ручка создания/получения заказа/листа заказов

    ACCEPT_ORDER = '/api/v1/orders/accept/:id'

    TRACK_ORDER = '/api/v1/orders/track'  # Ручка получения заказа по трек-номеру (GET)


class StaticData:
    STATIONS_ROKOSOVSKOGO_CHERKIZOVSKAYA = ["1", "2"]
    STATION_KALUZHSKAYA = ["110"]
    LIMIT_PAGE_DEFAULTS = {"limit": 10, "page": 0}

    LOGIN = 'Roman300920262047'
    PASSWORD = '12Roman34'
    FIRSTNAME = 'Roman'
    COURIER_ID = '814751'

    INCORRECT_ID_COURIER = '1000'

class Messages:
    # Создание курьера
    MESSAGE_DOUBLE_COURIER = 'Этот логин уже используется'
    MESSAGE_NOT_ENOUGH_DATA = 'Недостаточно данных для создания учетной записи'

    # Логин курьера
    MISSING_LOGIN_PASSWORD = 'Недостаточно данных для входа'
    INCORRECT_LOGIN_PASSWORD = 'Учетная запись не найдена'
    
    # Удаление курьера
    MISSING_ID_DEL = 'Недостаточно данных для удаления курьера' # Запрос без id:
    INCORRECT_ID_DEL = 'Курьера с таким id нет'                 # Запрос c несуществующим id:

    # Принятие заказа     
    
    MISSING_NUM = 'Недостаточно данных для поиска'              # Отсутствует номер заказа
    INCORRECT_NUM = 'Заказа с таким id не существует'           # Не существующий номер заказа
    INCORRECT_ID_COURIER = 'Курьера с таким id не существует'   # Запрос c несуществующим номер курьера:
    
    OLD_ORDER = 'Этот заказ уже в работе'                       # Заказ уже был в работе:
        
    # Получение заказа по треку
    MISSING_TRACK = 'Недостаточно данных для поиска'  # Запрос без номера заказа
    INCORRECT_TRACK = 'Заказ не найден'               # Запрос с несуществующим номером

class Cods:
    # Логин курьера
    SUCCESSFUL_LOGIN =  200         # Код получаемый в случае удачного логина курьера
    MISSING_LOGIN_PASSWORD = 400    # Код получаемый если не передать логин или пароль
    INCORRECT_LOGIN_PASSWORD = 404  # Код получаемый если передать некорректный логин или пароль

    # создание заказа
    SUCCESSFUL_ORDER = 201

    # Список заказов
    SUCCESSFUL_ORDER_LIST = 200     # Список закозов получен
    INCORRECT_ID_COURIER = 404      # Не найден курьер
    
    # Удаление курьера
    SUCCESSFUL_DEL = 200            # Успешное удаление курьера
    MISSING_ID_DEL = 400            # Запрос без id:
    INCORRECT_ID_DEL = 404          # Запрос c несуществующим id:

    # Принятие заказа
    ACCEPT_ORDER = 200              # Все хорошо
    MISSING_NUM = 400               # Отсутствует номер заказа
    INCORRECT_NUM = 404             # Не существующий номер заказа
    INCORRECT_ID_COURIER = 404      # Запрос c несуществующим номер курьера
    OLD_ORDER = 409                 # Заказ уже был в работе:
    NOT_ID_NOM = 400                # Нет id курьера или id заказа:

    # Получение заказа по треку
    SUCCESSFUL_TRACK = 200          # Заказ найден, возвращается объект с заказом
    MISSING_TRACK = 400             # Запрос без трек-номера (t не передан)
    INCORRECT_TRACK = 404           # Несуществующий трек-номер