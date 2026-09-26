# Pulse API

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-SQLite-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)

API REST de **hábitos + estado de ánimo** con persistencia **SQLite** (SQLModel/SQLAlchemy).

## Stack
- Python 3.11+
- FastAPI + Pydantic v2
- SQLModel + SQLite
- Uvicorn

## Endpoints
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Healthcheck |
| POST | `/entries` | Crear registro |
| GET | `/entries` | Listar (filtro `?habit=`) |
| GET | `/entries/{id}` | Detalle |
| DELETE | `/entries/{id}` | Borrar |
| GET | `/stats` | Agregados (moods, minutos) |

## Arranque
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Docs interactivas: http://127.0.0.1:8000/docs

## Ejemplo
```bash
curl -X POST http://127.0.0.1:8000/entries \
  -H "Content-Type: application/json" \
  -d "{\"habit\":\"lectura\",\"mood\":\"good\",\"minutes\":30,\"note\":\"Capítulo 3\"}"
```

## Autora
**Juliana Chantre Astudillo** · [GitHub](https://github.com/jchantre-jpg)
