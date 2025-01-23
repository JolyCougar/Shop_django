# Template shop


## Описание
Это готовый шаблон интернет магазина сделанного на Django.С использованием Юkassa для оплаты.С удобной панелью администратора, позваляющая пользователю из группы модератор<br>
отслеживать заказы, редактировать их статус, отправлять письмо от имени магазина.


## Функции
- Добавление новых задач
- Удаление задач
- Отметка задач как выполненных
- Создание расписания для автоочистки выполненых задач

## Установка
Для установки приложения выполните следующие шаги:

1.Для развертывания на своем компьютере:<br>
  1.1 Клонируйте репозиторий:<br>
     ```
       git clone https://github.com/JolyCougar/ToDo_app.git
       ```<br>
  1.2 Создайте файл .env с вашими переменными:<br>
   ```
      DJANGO_EMAIL_HOST='Укажите здесь smtp сервер вашей почты.'
      DJANGO_EMAIL_HOST_USER='Укажите здесь ваш Email.'
      DJANGO_EMAIL_HOST_PASSWORD='Укаэите здесь пароль который вам выдал сервер.'
      DJANGO_CELERY_BROKER_URL='redis://redis:6379/0' <- Здесь используется Redis как брокер, брокер запускается с помошью docker-compose.
      DJANGO_CELERY_RESULT_BACKEND='redis://redis:6379/0'
      DJANGO_CACHE_LOCATION='redis://redis:6379/0'
      DJANGO_CACHE_LIFE_MINUTES='Укажите время жизни кэша'
      SHOP_MONEY_SECRET_KEY='Укажите секретный пароль который выдал вам сервис Юкасса'
      SHOP_ID_KEY='Укажите ID который выдал вам сервис Юкасса'
      DJANGO_SECRET_KEY='Укажите здесь пароль для Django (Рандомный длинный пароль).'
      DJANGO_DEBUG='False' <- Флаг включения debug режима.
      DJANGO_ALLOWED_HOSTS='localhost 127.0.0.1 0.0.0.0' <- Добавьте ip адрес при необходимости, для определения списка допустимых хостов.
      DJANGO_ENGINE_DB='django.db.backends.postgresql'
      DJANGO_NAME_DB='Укажите имя БД указанный в .env.db'
      DJANGO_USER_DB='Укажите пользователя БД указанный в .env.db'
      DJANGO_PASSWORD_DB='Укажите пароль от БД указанный в .env.db'
      DJANGO_HOST_DB='db'
      DJANGO_PORT_DB='5432'
   ```
  1.3 Создайте файл .env.db с вашими переменными:<br>
```
  POSTGRES_USER='Укажите здесь пользователя который будет создан в БД'
  POSTGRES_PASSWORD='Укажите здесь пароль который будет создан в БД'
  POSTGRES_DB='Укажите название БД'
```
  1.4 Скачайте и установите docker и docker-compose [Установка Docker](https://docs.docker.com/engine/install/)<br>
  1.5 Перейдите в папку с проектом в комадной строке<br>
  1.6 Напишите команду:<br>
    ```
      docker-compose up --build
    ```<br>
  1.7 Приложение доступно по адресу localhost:80 или 127.0.0.1:80<br>
2. Для развертывания на сервере:<br>
  2.1 Создаем файлы из п. 1.2 и 1.3<br>
  2.2 Меняем имя файла default.conf в папке nginx в проекте, на default_dev.conf<br>
  2.3 Меняем имя файла prod.conf в папке nginx в проекте, на default.conf<br>
  2.4 Выполняем пункт 1.4<br>
  2.5 Запускаем проект командой:<br>
  ```
    docker-compose -f docker-compose.prod.yml up --build
  ```
  2.6 Проект будет доступен по адресу вашего сервера<br>
