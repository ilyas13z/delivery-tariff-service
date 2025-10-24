import json


async def test_create_package(client, get_package_from_database):
    package_data = {
        "name": "Package test no 1",
        "weight": 1.4,
        "price": 49.99,
        "type_id": 1,
    }
    resp = client.post("/package/", data=json.dumps(package_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200

    print("=+=" * 50, data_from_resp["package_id"], "=+=" * 50)

    users_from_db = await get_package_from_database(
        data_from_resp["package_id"]
    )
    print("=+=" * 50, users_from_db, "=+=" * 50)
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == package_data["name"]
    assert user_from_db["weight"] == package_data["weight"]
    assert user_from_db["price"] == package_data["price"]
    assert user_from_db["type_id"] == package_data["type_id"]
    assert user_from_db["price_delivery"] is None
    assert str(user_from_db["package_id"]) == data_from_resp["package_id"]
