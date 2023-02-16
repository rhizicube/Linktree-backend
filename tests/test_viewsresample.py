import json

def create_view(client):
    data1 = {"parameter": {"profile_link": "testtest", "username": "test0123", "profile_name": "Test User12", "profile_bio": "Test user's bio"}}
    response1 = client.post("/profile/", data=json.dumps(data1))
    profile_id = response1.json()["message"][8]
    data={"parameter": {"session_id": "123214","device_type": "view1device","view_count": 10,"profiles": profile_id}}
    response = client.post("/views/",data=json.dumps(data))
    assert response.status_code == 201
    assert response.json()["message"] == "View 1 created"

def create_view_invalid(client):
    response = client.post(
        "/views/",
        json={"parameter": {"session_id": "1","device_type": "view1","view_count": 10}}
    )
    assert response.status_code == 422

def get_views(client):
    response = client.get(
        "/views/"
    )
    assert response.status_code == 200

def get_view_by_id(client):
    response = client.get(
        "/views/",
        params={"view_id": 1}
    )
    assert response.status_code == 200

def get_view_by_id_invalid(client):
    response = client.get(
        "/api/views/views/",
        params={"view_id": 101}
    )
    assert response.status_code == 404


def update_view(client):
    data={"parameter": {"session_id": "123214sbxdsn","device_type": "viesmnxbw1device","view_count": 100,"profiles": 1}}
    response = client.put("/views/", params={"id": 1}, data=json.dumps(data))
    assert response.json() == {}
    assert response.status_code == 200

def update_view_invalid(client):
    data = {
  "parameter": {
    "session_id": "hsdbsn",
    "device_type": "sjdbxs",
    "view_count": 10,
    "profiles": 1
  }
}
    response = client.put(
        "/api/views/views/",
        params={"id": 101},
        data=json.dumps(data)
    )
    assert response.status_code == 404

def delete_view(client):
    response = client.delete(
        "/views/",
        params={"id": 1}
    )
    assert response.status_code == 200

def delete_view_invalid(client):
    response = client.delete(
        "/api/views/views/",
        params={"id": 101}
    )
    assert response.status_code == 404

def test_views(client):
    create_view(client)
    create_view_invalid(client)
    get_views(client)
    get_view_by_id(client)
    get_view_by_id_invalid(client)
    update_view(client)
    update_view_invalid(client)
    delete_view(client)
    delete_view_invalid(client)

