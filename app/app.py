import os

import psycopg
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_connection():
    """Oeffnet eine Verbindung zur PostgreSQL-Datenbank.
    Die Zugangsdaten kommen aus Umgebungsvariablen (docker-compose.yml / .env)."""
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def init_db():
    """Legt die Tabelle an, falls sie noch nicht existiert."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)


def row_to_todo(row):
    """Wandelt eine Datenbankzeile (Tupel) in ein Dictionary um."""
    return {
        "id": row[0],
        "title": row[1],
        "done": row[2],
    }


# GET /todos - alle Todos abrufen
@app.route("/todos", methods=["GET"])
def get_todos():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM todos ORDER BY id")
            rows = cur.fetchall()

    todos = []
    for row in rows:
        todos.append(row_to_todo(row))

    return jsonify(todos)


# POST /todos - neues Todo anlegen
@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object is required"}), 400

    title = data.get("title")

    if title is None:
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(title, str):
        return jsonify({"error": "Title must be a string"}), 400

    title = title.strip()

    if title == "":
        return jsonify({"error": "Title cannot be empty"}), 400

    sql = "INSERT INTO todos (title) VALUES (%s) RETURNING id, title, done"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (title,))
            row = cur.fetchone()

    return jsonify(row_to_todo(row)), 201


# DELETE /todos/<id> - Todo loeschen
@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
            if cur.rowcount == 0:
                return jsonify({"error": "Todo nicht gefunden!"}), 404

    return "", 204


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
