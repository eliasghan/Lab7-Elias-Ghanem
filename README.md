# Lab 7 - Python Testing

EECE 435L Software Tools Lab, Fall 2026-2027
Author: Elias Ghanem

Pytest tests for the Flask user management REST API built in Lab 5.

## Project structure

```
Lab7-Elias-Ghanem/
├── app.py                      Flask user API and SQLite functions (from Lab 5)
├── test_user_Elias_Ghanem.py   Graded tests for the user API
├── requirements.txt
├── postman/                    Lab 5 Postman collection and environment
└── tutorial/                   Lab 7 walkthrough exercises
    ├── capitalize.py
    ├── test_capitalize.py
    ├── wallet.py
    ├── test_wallet.py          Uses pytest fixtures
    ├── hello_add.py
    └── test_hello_add.py       Flask test client example
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Running the app

```bash
python app.py
```

On the first run, `init_db()` creates `database.db`, creates the `users` table
and inserts the default users listed in `DEFAULT_USERS`. Later runs keep the
existing data and do not insert the default users again.

## Running the tests

```bash
pytest
```

Each test gets its own temporary SQLite database (pytest `tmp_path` and
`monkeypatch` on `DB_PATH`), so the tests never touch `database.db` and can run
in any order.

## What is tested

| # | Function            | Tests |
|---|---------------------|-------|
| 1 | Database creation   | `init_db()` creates the file, the `users` table with the right columns, and the default users; a second run does not duplicate them |
| 2 | `insert_user()`     | New user gets the next id and is stored; missing fields return `{}` |
| 3 | `get_users()`       | Returns all users as a list of dicts; includes new users; empty list with no table |
| 4 | `get_user_by_id()`  | Returns the right user; unknown id returns `{}` |
| 5 | `update_user()`     | Updates only the target user; unknown id or missing fields return `{}` |
| 6 | `delete_user()`     | Removes the user; unknown id returns `Cannot delete user` |
| 7 | `api_get_user()`    | `GET /api/users/<id>` and `GET /api/users`: status 200 and returned JSON |
| 8 | `api_add_user()`    | `POST /api/users/add`: status 200, returned JSON, and the user is saved |
| 9 | `api_update_user()` | `PUT /api/users/update`: status 200, returned JSON, and the change is saved |
| 10 | `api_delete_user()` | `DELETE /api/users/delete/<id>`: status 200, status message, and the user is gone |
