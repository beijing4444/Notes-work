import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
import sqlite3
from typing import Generator



notes = [
    # {
    #     "id": 1,
    #     "title": "Азбука",
    #     "content": "Развивающий",
    # },
    # {
    #     "id": 2,
    #     "title": "AAA",
    #     "content": "123",
    # }
]


DB_NAME = "test.db"
app = FastAPI()

def get_db() -> Generator:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@app.get("/")
async def main():
    return FileResponse("new.html")

@app.get("/search_notes.html")
async def main():
    return FileResponse("search_notes.html")

@app.get("/add_notes.html")
async def main():
    return FileResponse("add_notes.html")

@app.get("/delete_notes")
async def main():
    return FileResponse("delete_notes.html")







@app.get("/notes", tags=["Заметки"])
def read_all_notes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()

    return [
        {"id": notes, "notes": notes,"content": "notes"}
        for notes in notes
    ]


    conn.close()
    return notes

@app.get("/notes/{id}", tags=["Выбор заметок"])
def read_note(id: int):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes WHERE id = ?", (id,))

    results = cursor.fetchone()
    conn.close()
    if results:
        return {"id": results[0], "name": results[1]}



    raise HTTPException(status_code=404, detail="Note not found")
#
# class NewNote(BaseModel):
#     title: str
#     content: str



@app.post("/notes", tags=["Добавить в заметки"])
def create_note(name: str, content: str, db: sqlite3.Connection = Depends(get_db)):
    # cursor.execute("SELECT * FROM notes WHERE name = ?", (name,content))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    a = name, content
    cursor.execute("INSERT INTO notes (name, content) VALUES (?,?)", a)
    conn.commit()

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    # if note_id not in notes:
    #     return {"error": "Item not found"}
    # del notes[note_id]
    # return {"message": "Note deleted successfully"}
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    conn.commit()
    conn.close()
    if cursor.rowcount > 0:
        return ("Элемент удален!")
    else:
        return ("Элемент не найден")



@app.put("/notes/{note_id}", tags=["Обновить заметку"])
def update_note(note_id: int, name: str, content: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET name = ? content = ?, WHERE id = ?", (name, content, note_id))
    conn.commit()
    conn.close()
    if cursor.rowcount > 0:
        return ("Элемент обнавлен!")
    else:
        return ("Элемент не найден!")





if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

