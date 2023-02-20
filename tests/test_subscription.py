import json
def create_subscription(client):
    data = {"parameter": {"subscription_name": "subscription1","subscription_type": "subscription1","subscription_description": "subscription1","subscription_reminder": True}}
    response = client.post("/subscriptions/",data=json.dumps(data))
    assert response.status_code == 201
    assert response.json()["message"] == "Subscription 1 created"

def create_subscription_invalid(client):
    response = client.post(
        "/subscriptions/",
        json={"parameter": {"subscription_name": "test1234"}}
    )
    assert response.status_code == 422

def get_subscription(client):
    response = client.get(
        "/subscriptions/"
    )
    assert response.status_code == 200



def get_subscription_by_id(client):
    response = client.get(
        "/subscriptions/",
        params={"subscription_id": 1}
    )
    assert response.status_code == 200

def get_subscription_by_id_invalid(client):
    response = client.get(
        "/api/subscriptions/subscriptions/",
        params={"subscription_id": 200}
    )
    assert response.status_code == 404

def update_subscription(client):
    # data1 = {"parameter": {"subscription_name": "subscripfertion1","subscription_type": "subscrfgrription1","subscription_description": "subscription1","subscription_reminder": True}}
    # response1 = client.post("/subscriptions/",data=json.dumps(data1))
    # sub_id = response1.json()["message"].split(" ")[1]
    data = {"parameter": {"subscription_type": "suhdbscription121","subscription_description": "subdjscription121","subscription_reminder": False}}
    response = client.put(
        "/subscriptions/",
        data=json.dumps(data),
        params={"id": 1}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Subscription 1 updated"

def update_subscription_invalid(client):
    data = {"parameter": {"subscription_name": "subscription1","subscription_type": "subscription1","subscription_description": "subscription1","subscription_reminder": True}}
    response = client.put(
        "/subscriptions/",
        data=json.dumps(data),
        params={"id": 200}
    )
    assert response.status_code == 404


def delete_subscription(client):
    response = client.delete(
        "/subscriptions/",
        params={"subscription_id": 1}
    )
    assert response.status_code == 200

def delete_subscription_invalid(client):
    response = client.delete(
        "/api/subscriptions/subscriptions/",
        params={"id": 200}
    )
    assert response.status_code == 404

def test_subscription(client):
    create_subscription(client)
    create_subscription_invalid(client)
    get_subscription(client)
    get_subscription_by_id(client)
    get_subscription_by_id_invalid(client)
    update_subscription(client)
    update_subscription_invalid(client)
    delete_subscription(client)
    delete_subscription_invalid(client)
