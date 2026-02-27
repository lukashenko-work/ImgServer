В локальном Docker (на твоем компе) ситуация забавнее: «внешний мир» — это ты сам и программы на твоем хосте.
Если ты хочешь, чтобы к API нельзя было постучаться через localhost:80 (Nginx), а фронтенд при этом работал, нужно понять: где выполняется код фронтенда?
# Вариант 1: Фронтенд на JS в браузере (React, Vue и т.д.)
Тут плохие новости: браузер — это клиент. Если браузер должен получить данные, он делает запрос со своего IP на твой Nginx. Nginx не может отличить твой браузер от соседа по Wi-Fi только по сети.
Что делать:
Используй valid_referers, но без none. Это запретит открывать API-ссылки просто в строке браузера.
nginx

location /api/ {
    valid_referers localhost; # разрешаем только если запрос инициирован с localhost
    if ($invalid_referer) {
        return 403;
    }
    proxy_pass http://api:8000;
}

Используйте код с осторожностью.
Но помни: любой запрос из Postman или curl с заголовком Referer: localhost всё равно пройдёт.
# Вариант 2: Фронтенд с SSR (Next.js, Nuxt) или бэкенд-шаблоны
Если страницу собирает сам контейнер (Server Side), то тебе вообще не нужно выставлять API в Nginx.

    В Docker Compose: убери ports у API.
    В Nginx: убери location /api/.
    Во фронтенде: делай запросы на http://api:8000.
    Итог: API доступно только внутри сети Docker, а снаружи (через браузер или localhost) его вообще не существует.

# Вариант 3: «Костыль» для локальной разработки (IP хоста)
Если ты хочешь разрешить доступ к API через Nginx только для своего Docker-контейнера фронтенда, можно заблокировать всех, кроме внутренней сети Docker:
nginx

location /api/ {
    allow 172.16.0.0/12; # Стандартная внутренняя сеть Docker
    deny all;            # Всех остальных (включая тебя на хосте) — в бан
    proxy_pass http://api:8000;
}

Используйте код с осторожностью.
В этом случае, если ты сам введешь в браузере http://localhost/api/data, ты получишь 403, потому что для Docker твой запрос пришел с "внешнего" шлюза (172.x.x.1), а не изнутри сети.
# Короче:

    Если API дергает браузер — на 100% не закроешься (используй CORS + Referer).
    Если API дергает другой контейнер — просто не прописывай location /api/ в конфиге Nginx.

# Настройка CORS заголовков в Nginx (если надо) на примере LiveServer port 5500
Настройка Nginx в Docker
В твоем nginx.conf (который проброшен в контейнер) нужно жестко ограничить реферер и настроить CORS, иначе браузер просто не покажет данные.
nginx

server {
    listen 80;

    location /api/ {
        # 1. ЗАПРЕЩАЕМ ВСЁ, КРОМЕ LIVE SERVER
        # Убираем 'none' и 'blocked' — это закроет доступ через адресную строку браузера
        valid_referers http://localhost:5500 http://127.0.0.1:5500;

        if ($invalid_referer) {
            return 403;
        }

        # 2. РАЗРЕШАЕМ CORS (обязательно для Live Server)
        add_header 'Access-Control-Allow-Origin' 'http://localhost:5500' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

        # Обработка OPTIONS запросов (браузер шлет их перед POST/PUT)
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        # 3. ПРОКСИРУЕМ НА ТВОЙ API
        # Если API в том же Docker-compose, пиши имя сервиса
        proxy_pass http://api_container:8000/;
    }
}

# Локально без Nginx, настройка CORS в python
Если ты хочешь сделать это
вообще без Nginx, только силами своего бэкенда (Python, Node.js, Go и т.д.), запущенного в Docker, то логика valid_referers переносится в код твоего API.
Nginx — это просто удобный фильтр, но твой бэкенд точно так же видит все заголовки.
Как это реализовать (логика):
Чтобы закрыть доступ всем, кроме Live Server, тебе нужно проверять заголовок запроса Referer (или Origin) прямо в коде API.
Пример на Python (FastAPI/Flask):
python

from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

@app.middleware("http")
async def restrict_referer(request, call_next):
    referer = request.headers.get("referer")
    # Разрешаем только если запрос пришел с порта Live Server
    if not referer or not referer.startswith("http://localhost:5500"):
        raise HTTPException(status_code=403, detail="Access denied")
    return await call_next(request)

Почему это работает:

    Прямой заход: Если ты вставишь URL в браузер, заголовок Referer будет пустым. Твой код увидит это и выдаст 403.
    Live Server: Когда JS с localhost:5500 делает запрос, браузер обязан прикрепить заголовок Referer: http://localhost:5500/. Код его пропустит.

# Итого:

    - Nginx делает эту проверку «на входе», не нагружая само приложение.

    - Без Nginx ты делаешь то же самое внутри кода API, проверяя request.headers['referer'].
    
    В обоих случаях защиту можно обойти через curl -H "Referer: http://localhost:5500", но от обычных пользователей и случайных заходов это защитит.
