release: python manage.py migrate --no-input
web: bin/start-pgbouncer daphne QuizSite.asgi:application --port $PORT --bind 0.0.0.0
