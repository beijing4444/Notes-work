import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
import sqlite3




notes = [
    {
        "id": 1,
        "title": "Азбука",
        "content": "Развивающий",
    },
    {
        "id": 2,
        "title": "AAA",
        "content": "123",
    }
]


DB_NAME = "test.db"
app = FastAPI()



def create_table():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        content TEXT
    )
    ''')

    conn.commit()
    conn.close()



def add_note():
    name = input("Введите название: ")
    content = input("Описание: ")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (name, content) VALUES (?,?)", (name, content))
    conn.commit()
    conn.close()
    print("Заметка добавлена!")


def get_notes():
    try:
        note_id = int(input("Ввежите ID для поиска: "))
    except ValueError:
        print("Неверный формат, ID должен быть числом !")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))

    results = cursor.fetchone()
    conn.close()

    if results:
        print(f"ID: {results[0]}, Название: {results[1]}, Описание: {results[2]}")
    else:
        print("Заметка не найдена")






def update_note():
    try:
        note_id = int(input("Введите ID для изменения: "))
    except ValueError:
        print("ID должен быть числом!")
        return

    name = input("Введите новое название: ")
    content = input("Новое описание: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("UPDATE notes SET name = ?, content = ? WHERE id = ?", (name, content, note_id))

    conn.commit()
    conn.close()

    if cursor.rowcount > 0:
        print("Элемент обнавлен!")
    else:
        print("Элемент не найден")

def delete_note():
    try:
        note_id = int(input("Введите ID для удаления: "))
    except ValueError:
        print("ID должен быть числом")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    conn.commit()
    conn.close()

    if cursor.rowcount > 0:
        print("Элемент удален!")
    else:
        print("Элемент не найден")

def main():
    create_table()

    while True:
        print("\n1. Добавить")
        print("2. Найти")
        print("3. Изменить")
        print("4. Удалить")
        print("5. Выход")

        choice = input("Выберите команду: ")

        if choice == "1":
            add_note()
        elif choice == "2":
            get_notes()
        elif choice == "3":
            update_note()
        elif choice == "4":
            delete_note()
        elif choice == "5":
            break
        else:
            print("Неверная команда")




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
    return notes

@app.get("/notes/{id}", tags=["Выбор заметок"])
def read_note(id: int):
    for note in notes:
        if note["id"] == id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")

class NewNote(BaseModel):
    title: str
    content: str





@app.post("/notes", tags=["Добавить в заметки"])
def create_note(note: NewNote):
    notes.append(
        {
            "id": len(notes) + 1,
            "title": note.title,
            "content": note.content,
        }
    )
    return {"success": True}

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    if note_id not in notes:
        return {"error": "Item not found"}
    del notes[note_id]
    return {"message": "Note deleted successfully"}







if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

