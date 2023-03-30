# Распределенная система

## Полезные ссылки
- ***python dependency injector*** - https://python-dependency-injector.ets-labs.org/examples/fastapi.html
- ***FastAPI*** - https://fastapi.tiangolo.com/
- ***SqlAlchemy(v 1.4)*** - https://docs.sqlalchemy.org/en/14/

## Архитектура

### Верний уровень
- __*docker/*__ - Контейнеры приложения
- __*app/*__ - приложение
- __*images*__ - для работы с изображениями
- __*main.py*__ - запуск

### Приложение

#### app/kernel

<p>В модулях <i><b>database.py и redis.py</b></i> обеспечивается подключение к источникам хранения информации</p>
<p><i><b>container.py</b></i> - отвечает за создание объектов приложения, также обеспечивается dependency inversion</p>

#### app/database

- repository - отвечает за запросы
- model - модели БД

#### app/http

- controllers - В контроллерах происходит dependency inversion, контроллер выплняет роль модуля
- middleware - проверка прав на доступ к тому или иному модулю
- services - Бизнес логика + Подключение сервисов