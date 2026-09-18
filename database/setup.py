import sqlite3


def init_db():
    db = sqlite3.connect("database/app.db")

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
