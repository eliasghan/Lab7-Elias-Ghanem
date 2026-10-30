import sqlite3

import pytest
from flask import json

import app as user_app


NEW_USER = {
    "name": "Elias Ghanem",
    "email": "eliasghanem@gmail.com",
    "phone": "03987654",
    "address": "Bliss Street, Beirut",
    "country": "Lebanon",
}

UPDATED_USER = {
    "user_id": 2,
    "name": "Jane Smith",
    "email": "jane.smith@aub.edu.lb",
    "phone": "03111222",
    "address": "Makdessi Street, Beirut",
    "country": "Lebanon",
}


def default_user(user_id):
    return {"user_id": user_id, **user_app.DEFAULT_USERS[user_id - 1]}


def without_id(user):
    return {key: value for key, value in user.items() if key != "user_id"}


def get_json(response):
    return json.loads(response.get_data(as_text=True))


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "database.db"
    monkeypatch.setattr(user_app, "DB_PATH", str(path))
    return path


@pytest.fixture
def seeded_db(db_path):
    user_app.init_db()
    return db_path


@pytest.fixture
def client(seeded_db):
    user_app.app.config["TESTING"] = True
    return user_app.app.test_client()


def test_database_created_with_default_users_on_first_run(db_path):
    assert not db_path.exists()

    users = user_app.init_db()

    assert db_path.exists()
    assert [user["user_id"] for user in users] == [1, 2, 3]
    assert [without_id(user) for user in users] == user_app.DEFAULT_USERS


def test_database_users_table_columns(seeded_db):
    conn = sqlite3.connect(seeded_db)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
    conn.close()

    assert columns == ["user_id", "name", "email", "phone", "address", "country"]


def test_database_not_seeded_twice_on_second_run(seeded_db):
    assert user_app.create_db_table() is False

    users = user_app.init_db()

    assert len(users) == len(user_app.DEFAULT_USERS)


def test_insert_user(seeded_db):
    inserted = user_app.insert_user(NEW_USER)

    assert inserted["user_id"] == 4
    assert without_id(inserted) == NEW_USER
    assert user_app.get_user_by_id(4) == inserted
    assert len(user_app.get_users()) == 4


def test_insert_user_with_missing_fields(seeded_db):
    assert user_app.insert_user({"name": "No Email"}) == {}
    assert len(user_app.get_users()) == 3


def test_get_users(seeded_db):
    users = user_app.get_users()

    assert isinstance(users, list)
    assert users == [default_user(1), default_user(2), default_user(3)]


def test_get_users_after_insert(seeded_db):
    inserted = user_app.insert_user(NEW_USER)

    users = user_app.get_users()

    assert len(users) == 4
    assert users[-1] == inserted


def test_get_users_without_table(db_path):
    assert user_app.get_users() == []


def test_get_user_by_id(seeded_db):
    assert user_app.get_user_by_id(1) == default_user(1)
    assert user_app.get_user_by_id(2) == default_user(2)
    assert user_app.get_user_by_id(3) == default_user(3)


def test_get_user_by_id_unknown(seeded_db):
    assert user_app.get_user_by_id(99) == {}


def test_update_user(seeded_db):
    updated = user_app.update_user(UPDATED_USER)

    assert updated == UPDATED_USER
    assert user_app.get_user_by_id(2) == UPDATED_USER
    assert user_app.get_user_by_id(1) == default_user(1)
    assert user_app.get_user_by_id(3) == default_user(3)


def test_update_user_unknown(seeded_db):
    assert user_app.update_user({**UPDATED_USER, "user_id": 99}) == {}
    assert len(user_app.get_users()) == 3


def test_update_user_with_missing_fields(seeded_db):
    assert user_app.update_user({"user_id": 2, "name": "Only Name"}) == {}
    assert user_app.get_user_by_id(2) == default_user(2)


def test_delete_user(seeded_db):
    assert user_app.delete_user(1) == {"status": "User deleted successfully"}
    assert user_app.get_user_by_id(1) == {}
    assert user_app.get_users() == [default_user(2), default_user(3)]


def test_delete_user_unknown(seeded_db):
    assert user_app.delete_user(99) == {"status": "Cannot delete user"}
    assert len(user_app.get_users()) == 3


def test_api_get_users(client):
    response = client.get("/api/users")
    data = get_json(response)

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert data == [default_user(1), default_user(2), default_user(3)]
    assert "John Doe" in str(response.data)


def test_api_get_user(client):
    response = client.get("/api/users/1")
    data = get_json(response)

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert data == default_user(1)


def test_api_get_user_unknown(client):
    response = client.get("/api/users/99")

    assert response.status_code == 200
    assert get_json(response) == {}


def test_api_add_user(client):
    response = client.post(
        "/api/users/add",
        data=json.dumps(NEW_USER),
        content_type="application/json",
    )
    data = get_json(response)

    assert response.status_code == 200
    assert data["user_id"] == 4
    assert without_id(data) == NEW_USER
    assert user_app.get_user_by_id(4) == data
    assert get_json(client.get("/api/users/4")) == data


def test_api_add_user_with_missing_fields(client):
    response = client.post(
        "/api/users/add",
        data=json.dumps({"name": "No Email"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert get_json(response) == {}
    assert len(user_app.get_users()) == 3


def test_api_update_user(client):
    response = client.put(
        "/api/users/update",
        data=json.dumps(UPDATED_USER),
        content_type="application/json",
    )
    data = get_json(response)

    assert response.status_code == 200
    assert data == UPDATED_USER
    assert user_app.get_user_by_id(2) == UPDATED_USER
    assert get_json(client.get("/api/users/2")) == UPDATED_USER


def test_api_update_user_unknown(client):
    response = client.put(
        "/api/users/update",
        data=json.dumps({**UPDATED_USER, "user_id": 99}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert get_json(response) == {}


def test_api_delete_user(client):
    response = client.delete("/api/users/delete/2")

    assert response.status_code == 200
    assert get_json(response) == {"status": "User deleted successfully"}
    assert user_app.get_user_by_id(2) == {}
    assert get_json(client.get("/api/users")) == [default_user(1), default_user(3)]


def test_api_delete_user_unknown(client):
    response = client.delete("/api/users/delete/99")

    assert response.status_code == 200
    assert get_json(response) == {"status": "Cannot delete user"}
    assert len(user_app.get_users()) == 3
