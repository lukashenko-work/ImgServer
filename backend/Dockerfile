FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY --exclude=env-presets . .
# COPY --exclude=env-presets --exclude=logs --exclude=uploads . .
# COPY . .

COPY ./env-presets/test.env ./.env

EXPOSE 8000

CMD [ "python", "app.py" ]

# добавить .env в игнор