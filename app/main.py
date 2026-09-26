"""
Pulse API — REST de hábitos / estado de ánimo con SQLite.
Ejecutar: python -m venv .venv && .venv/Scripts/activate && pip install -r requirements.txt && uvicorn app.main:app --reload
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField, Session, SQLModel, create_engine, select

DB_URL = "sqlite:///./pulse.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


class Mood(str, Enum):
    great = "great"
    good = "good"
    ok = "ok"
    low = "low"
    rough = "rough"


class EntryBase(SQLModel):
    habit: str = SQLField(index=True, min_length=1, max_length=64)
    mood: Mood
    note: Optional[str] = SQLField(default=None, max_length=280)
    minutes: int = SQLField(default=0, ge=0, le=24 * 60)


class Entry(EntryBase, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    created_at: datetime = SQLField(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
    )


class EntryCreate(EntryBase):
    pass


class EntryRead(EntryBase):
    id: int
    created_at: datetime


class StatsOut(BaseModel):
    total_entries: int
    unique_habits: int
    avg_minutes: float
    mood_breakdown: dict[str, int]


app = FastAPI(
    title="Pulse API",
    description="API de hábitos y mood con SQLite — Juliana Chantre",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "pulse-api"}


@app.post("/entries", response_model=EntryRead, status_code=201)
def create_entry(payload: EntryCreate) -> Entry:
    with Session(engine) as session:
        row = Entry.model_validate(payload)
        session.add(row)
        session.commit()
        session.refresh(row)
        return row


@app.get("/entries", response_model=list[EntryRead])
def list_entries(
    habit: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[Entry]:
    with Session(engine) as session:
        stmt = select(Entry).order_by(Entry.created_at.desc()).limit(limit)
        if habit:
            stmt = stmt.where(Entry.habit == habit)
        return list(session.exec(stmt).all())


@app.get("/entries/{entry_id}", response_model=EntryRead)
def get_entry(entry_id: int) -> Entry:
    with Session(engine) as session:
        row = session.get(Entry, entry_id)
        if not row:
            raise HTTPException(404, "Entry not found")
        return row


@app.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int) -> None:
    with Session(engine) as session:
        row = session.get(Entry, entry_id)
        if not row:
            raise HTTPException(404, "Entry not found")
        session.delete(row)
        session.commit()


@app.get("/stats", response_model=StatsOut)
def stats() -> StatsOut:
    with Session(engine) as session:
        rows = list(session.exec(select(Entry)).all())
    moods: dict[str, int] = {}
    habits = set()
    total_min = 0
    for r in rows:
        moods[r.mood.value] = moods.get(r.mood.value, 0) + 1
        habits.add(r.habit)
        total_min += r.minutes
    n = len(rows)
    return StatsOut(
        total_entries=n,
        unique_habits=len(habits),
        avg_minutes=round(total_min / n, 2) if n else 0.0,
        mood_breakdown=moods,
    )
