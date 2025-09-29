# Data Engineering ETL Pipeline with Dashboard

Проект для извлечения, трансформации и загрузки данных о постах пользователей с веб-дашбордом

## Быстрый старт

```bash
chmod +x run.sh && ./run.sh
```

## Просмотр результатов

- **Дашборд**: http://localhost:8000/top
- **Логи ETL**: `docker-compose logs -f etl`

## Тестирование

```bash
docker-compose exec etl pytest tests/ -v
docker-compose exec etl ruff check src/ tests/
```

## Cron расписание
```
- Extract: каждые 5 минут
- Transform: каждые 10 минут
```

### **.env.example** (шаблон для переменных окружения)

```env
# Database configuration
DB_HOST=db
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=password

# API configuration
API_URL=https://jsonplaceholder.typicode.com/posts

# Dashboard configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8000
```

## 📊 Структура репозитория:
```
de-project/
├── .gitignore
├── README.md
├── .env.example
├── .ruff.toml
├── pytest.ini
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.dashboard
├── requirements.txt
├── requirements-test.txt
├── requirements-dashboard.txt
├── run.sh
├── cronjobs
├── scripts/
│   ├── extract.py
│   └── transform.py
├── dashboard/
│   ├── app.py
│   ├── index.html
│   └── style.css
├── tests/
│   ├── test_extract.py
│   └── test_transform.py
├── sql/
│   └── init.sql
└── logs/
    └── .gitkeep
```
