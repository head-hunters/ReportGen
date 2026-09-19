import sqlite3


def init_db():
    db = sqlite3.connect("database/app.db")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
        
        CREATE TABLE projects (
            project_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT,
            name TEXT,
            dept TEXT,
            abstract TEXT,
            description TEXT,
            survey TEXT,
            technologies TEXT,
            duration TEXT,
            additional TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE modules (
            module_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            module_number INTEGER NOT NULL,
            name TEXT,
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        );
    """)

    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
