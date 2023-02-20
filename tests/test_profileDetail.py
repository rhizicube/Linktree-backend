import json
def create_profileDetail(client):
    data={
    "profile": {
        "profile_link": "random",
        "profile_name": "User01",
        "username": "test012",
        "profile_bio": "This is where user can put any description they like"
    },
    "setting": {
        "profile_social": {
            "Instagram": "https://www.instagram.com/user01/"
        }
    },
    "link": {
            "link_name": "My Music",
            "link_url": "https://www.smule.com/user01/",
            "link_enable": True,
            "profile_id": 1
        }
}
    response = client.post("/savedetails/",data=json.dumps(data), params={"username": "test012"})
    assert response.json()["message"] == "Profile details saved"
    assert response.status_code == 201
    

# round 1
# profile like is everything after "port/"
# User side
# test 1: create profile
# test 2: create link
# test 3: create setting
# test 4: create setting for a new username, to give appropriate error message
# test 5: call getalldetails/ and verify if the data matches
# test 6: modify profile, link, and setting individually call getalldetails/ and verify if the modified data matches, and the rest is unchanged

# def update_profile(client):
#     response = client.put(
#         "/updatedetails/",
#         json={
#             "profile": {
#                 "profile_link": "https://linktr.ee/random",
#                 "profile_name": "User01",
#                 "profile_bio": "This is where user can put any description they like1"
#             }
#         },
#         params={"username": "testuser1"},
#     )
#     assert response.json() == {}
#     assert response.status_code == 201

def create_profile_only(client):
    data = {"profile": {"profile_link": "random20567","profile_name": "UserTest01","profile_bio": "This is where user can put any description they like", "username": "test0123"}}
    response = client.post("/savedetails/",data=json.dumps(data), params={"username": "test0123"})
    assert response.json()["message"] == "Profile details saved"
    assert response.status_code == 201

def create_link_only(client):
    data = {
    "link": 
        {
            "link_name": "My Music",
            "link_url": "https://www.smule.com/user012345/",
            "link_enable": True,
            "profile_id": 1
        }
    
    
}
    response = client.post(
        "/savedetails/",
        data=json.dumps(data), params={"username": "test012"})
    assert response.json()["message"] == "Profile details saved"
    assert response.status_code == 201

def create_setting_only(client):
    data={
    "setting": {
            "profile_social": {
                "Instagram": "https://www.instagram.com/user01/"
            }
        }
}
    response = client.post(
        "/savedetails/",data = json.dumps(data), params={"username": "test012"})
    assert response.json()["message"] == "Profile details saved"
    assert response.status_code == 201

def create_setting_with_invalid_username(client):
    data={
    "setting": {
            "profile_social": {
                "Instagram": "https://www.instagram.com/user01hhvh/"
            }
        }
}
    response = client.post(
        "/savedetails/",data = json.dumps(data), params={"username": "bncvfgd"})
    assert response.status_code == 400

def update_profile(client):
    data={"profile": 
            {
                "profile_bio": "This is kjdje where user can put any description they like12"
            }
        }
    response = client.put("/updatedetails/",data=json.dumps(data),params={"username": "test012"})
    assert response.json()["message"] == "Profile details updated"
    assert response.status_code == 200

def update_link(client):
    data = {"link":
        {
            "link_enable": False
        }}
    response = client.put("/updatedetails/", data=json.dumps(data), params={"username":"test012"})
    assert response.json()["message"] == "Profile details updated"
    assert response.status_code == 200

def update_setting(client):
    data = {"setting": {"profile_social": {"Instagram": "https://www.ig.com/user0123456/"}}}
    response = client.put("/updatedetails/", data=json.dumps(data), params={"username":"test012"})
    assert response.json()["message"] == "Profile details updated"
    assert response.status_code == 200

def create_profileDetail_invalid(client):
    response = client.post(
        "/savedetails/",
        json={"profile": {"profile_name": "test1234"}}
    )
    assert response.status_code == 422

def get(client):
    data = {"data":{"link": {
            "link_name": "My Music",
            "link_url": "https://www.smule.com/user01/",
            "link_enable": True,
            "profile_id": 1
        },"profile": {
        "profile_link": "random",
        "profile_name": "User01",
        "username": "test012",
        "profile_bio": "This is where user can put any description they like"
    },
    "setting": {
        "profile_social": {
            "Instagram": "https://www.instagram.com/user01/"
        }
    },
    }}
    response = client.get("/getalldetails/", params={"username": "test012"})
    assert response.json()["data"]["profile"]["profile_name"] == "User01"
    assert response.json()["data"]["profile"]["profile_bio"] == "This is where user can put any description they like"
    assert response.json()["data"]["profile"]["profile_link"] == "random"
    assert response.json()["data"]["profile"]["username"] == "test012"
    assert response.status_code == 200


def get_invalid(client):
    response = client.get(
        "/getalldetails/", params={"username": "testujbhvser2"}
    )
    assert response.status_code == 400

def test_profileDetails(client):
    create_profileDetail(client)
    get(client)
    create_setting_only(client)
    update_setting(client)
    update_link(client)
    create_link_only(client)
    create_profile_only(client)
    update_profile(client)
    create_setting_with_invalid_username(client)
    create_profileDetail_invalid(client)
    get_invalid(client)
