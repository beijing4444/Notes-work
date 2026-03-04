import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Generator

DB_NAME = "test.db"

app = FastAPI(title="Notes API")


# --------------------
# Создаём таблицу сразу при запуске файла
# --------------------

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()


create_table()  # вызываем функцию сразу


# --------------------
# Dependency подключения
# --------------------

def get_db() -> Generator:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# --------------------
# Модель данных
# --------------------

class Note(BaseModel):
    name: str
    content: str


# --------------------
# CRUD
# --------------------

@app.post("/notes")
def add_note(note: Note, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO notes (name, content) VALUES (?, ?)",
        (note.name, note.content)
    )
    db.commit()
    return {"message": "Заметка добавлена!"}


@app.get("/notes")
def get_all_notes(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


@app.get("/notes/{note_id}")
def get_note(note_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    result = cursor.fetchone()

    if result:
        return dict(result)
    else:
        raise HTTPException(status_code=404, detail="Заметка не найдена")


@app.put("/notes/{note_id}")
def update_note(note_id: int, note: Note, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE notes SET name = ?, content = ? WHERE id = ?",
        (note.name, note.content, note_id)
    )
    db.commit()

    if cursor.rowcount > 0:
        return {"message": "Элемент обновлён!"}
    else:
        raise HTTPException(status_code=404, detail="Элемент не найден")


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()

    if cursor.rowcount > 0:
        return {"message": "Элемент удалён!"}
    else:
        raise HTTPException(status_code=404, detail="Элемент не найден")


# --------------------
# Запуск
# --------------------

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)