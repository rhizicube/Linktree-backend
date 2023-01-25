import json
def create_profileDetail(client):
    data={
    "profile": {
        "profile_link": "https://linktr.ee/random",
        "profile_name": "User01",
        "username": "test012",
        "profile_bio": "This is where user can put any description they like"
    },
    "setting": {
        "profile_social": {
            "Instagram": "https://www.instagram.com/user01/"
        }
    },
    "link": [
        {
            "link_name": "My Music",
            "link_url": "https://www.smule.com/user01/",
            "link_enable": True,
            "profile_id": 1
        }
    ]
}
    response = client.post("/savedetails/",data=json.dumps(data), params={"username": "testuser1"})
    assert response.status_code == 201

def create_profileDetail_invalid(client):
    response = client.post(
        "/savedetails/",
        json={"parameter": {"profile_name": "test1234"}}
    )
    print(response.json())
    assert response.status_code == 422

def get(client):
    response = client.get(
        "/getalldetails/", params={"username": "testuser1"}
    )
    assert response.status_code == 200

def get_invalid(client):
    response = client.get(
        "/getalldetails/", params={"username": "testujbhvser2"}
    )
    assert response.status_code == 400

def test_profileDetails(client):
    create_profileDetail(client)
    create_profileDetail_invalid(client)
    get(client)
    get_invalid(client)
    