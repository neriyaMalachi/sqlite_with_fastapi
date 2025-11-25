from fastapi import FastAPI
import sqlite3

app = FastAPI()

# שם הקובץ של SQLite
DB_PATH = "school.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# דוגמה לטבלה:
# CREATE TABLE students (
#   id INTEGER PRIMARY KEY,
#   name TEXT,
#   age INTEGER
# );

@app.get("/students")
def get_students():
    conn = get_connection()

    # מאפשר החזרה כמילון
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # this for create data in db
    # cur.execute("CREATE TABLE IF NOT EXISTS students (  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER)")
    # cur.execute("INSERT INTO students (name, age) VALUES('Neriya', 23),('David', 30),('Moshe', 19),('Shira', 27),('Yael', 22);")
    # conn.commit()

    cur.execute("SELECT id, name, age FROM students")
    rows = cur.fetchall()

    conn.close()

    # המרה לרשימה של dict
    result = [dict(row) for row in rows]
    return result


@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, name, age FROM students WHERE id = ?", (student_id,))
    row = cur.fetchone()

    conn.close()

    if row is None:
        return {"error": "Student not found"}

    return dict(row)
