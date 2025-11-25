from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import sqlite3

app = FastAPI()

# שם הקובץ של SQLite
DB_PATH = "school.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# ---------- Models (Pydantic) ----------
class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    age: int | None = Field(default=None, ge=0)

class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    age: int | None = Field(default=None, ge=0)

# ---------- Startup: ensure table ----------
@app.on_event("startup")
def ensure_table():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER
        )
        """)
        conn.commit()
    finally:
        conn.close()

# ---------- READ: list all ----------
@app.get("/students")
def get_students():
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # מאפשר החזרה כמילון
    cur = conn.cursor()

    cur.execute("SELECT id, name, age FROM students")
    rows = cur.fetchall()
    conn.close()

    result = [dict(row) for row in rows]
    return result

# ---------- READ: get by id ----------
@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, name, age FROM students WHERE id = ?", (student_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    return dict(row)

# ---------- CREATE ----------
@app.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO students (name, age) VALUES (?, ?)",
            (payload.name, payload.age)
        )
        conn.commit()
        new_id = cur.lastrowid

        # מחזירים את הרשומה החדשה
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, name, age FROM students WHERE id = ?", (new_id,))
        row = cur.fetchone()
        return dict(row)
    finally:
        conn.close()

# ---------- UPDATE (PUT = החלפה מלאה) ----------
@app.put("/students/{student_id}")
def update_student_put(student_id: int, payload: StudentCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE students SET name = ?, age = ? WHERE id = ?",
            (payload.name, payload.age, student_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        # מחזירים אחרי עדכון
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, name, age FROM students WHERE id = ?", (student_id,))
        row = cur.fetchone()
        return dict(row)
    finally:
        conn.close()

# ---------- DELETE ----------
@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        # 204 בלי גוף
        return
    finally:
        conn.close()
