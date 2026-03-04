import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from typing import List
from contextlib import asynccontextmanager

DB_NAME = "test.db"


# ---------- LIFESPAN ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()
    yield


app = FastAPI(lifespan=lifespan)


# ---------- DATABASE ----------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---------- MODELS ----------

class NoteCreate(BaseModel):
    title: str
    content: str


class Note(BaseModel):
    id: int
    title: str
    content: str


# ---------- ROUTES ----------

@app.get("/notes", response_model=List[Note])
def get_notes(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    return [dict(note) for note in notes]


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return dict(note)


@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (note.title, note.content)
    )
    db.commit()

    new_id = cursor.lastrowid
    return {"id": new_id, "title": note.title, "content": note.content}


@app.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE notes SET title = ?, content = ? WHERE id = ?",
        (note.title, note.content, note_id)
    )
    db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"message": "Note updated"}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"message": "Note deleted"}


if __name__ == "__test__":
    uvicorn.run("main:app", reload=True)