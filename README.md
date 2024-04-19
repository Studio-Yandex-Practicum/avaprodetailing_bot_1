# Описание проекта
Бот для детейлинг мастерской AVAPRODETAILING
## Заполнить:
1. Сведения о команде
2. Описание проекта
3. Инструкция по сборке и запуску
4. Стэк технологий
5. Ссылки на сторонние фреймворки, библиотеки, иконки и шрифты если использовались.


### Запуск проекта (на сервере через workflow)

- Клонирование репозитория:
Скопируйте репозиторий в свой аккаунт GitHub, нажав кнопку Fork.
- Настройка:
Перейдите в раздел Settings -> Secrets and Variables -> Actions в вашем репозитории.
Добавьте следующие секреты:
    `DOCKER_USERNAME` и `DOCKER_PASSWORD` - ваши учетные данные с Docker Hub.
    `HOST` - IP адрес вашего сервера, где будет развернуто приложение.
    `USER` - имя пользователя на сервере.
    `SSH_KEY` - приватный SSH ключ для подключения к серверу.
    `PASSPHRASE` - пароль для вашего SSH ключа.
- Корректировка конфигурации:
    Отредактируйте файл infra/docker-compose.yaml, указав ваш аккаунт в Docker Hub в качестве префикса для image.
    Создайте файл .env в корневой директории проекта, используя файл env.example в качестве шаблона.
- Перенос файлов на сервер:
    Скопируйте следующие файлы на ваш сервер в домашнюю директорию ~/avaprodetailing/:
    infra/docker-compose.yaml
    infra/nginx.conf (в директорию nginx)
    .env
- Запуск проекта:
    После переноса файлов на сервер проект будет автоматически запущен при отправке (push) изменений в вашем репозитории на GitHub.

### Настройки на сервере:
- Установить docker compose
- Установить nginx
    - указать в nginx.conf настройки для reverse proxy на порт 8081 (который указан в docker-compose.yaml)
    - указать имя домена
- Установить SSL-сертификат на домен:
    ```
    sudo apt install snapd
    sudo snap install core; sudo snap refresh core
    sudo snap install --classic certbot
    sudo ln -s /snap/bin/certbot /usr/bin/certbot
    sudo apt install certbot
    sudo certbot --nginx -d <имя домена>
    ```

- PGAdmin будет настроен на порту 8088 `http://<имя домена>:8088`
- Документация swagger доступна по адресу `https://<имя домена>:/docs`
