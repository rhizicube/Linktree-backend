import json
def create_profileDetail(client):
    data={
    "profile": {
        "profile_link": "https://linktr.ee/random", # profile like is everything after "port/"
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
    response = client.post("/savedetails/",data=json.dumps(data), params={"username": "testuser1"}) # check case if link/setting is posted before profile is created
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
    assert response.status_code == 200 # check content too

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







# round 1
# profile like is everything after "port/"
# User side
# test 1: create profile
# test 2: create link
# test 3: create setting
# test 4: create setting for a new username, to give appropriate error message
# test 5: call getalldetails/ and verify if the data matches
# test 6: modify profile, link, and setting individually call getalldetails/ and verify if the modified data matches, and the rest is unchanged


# round 2
# Test uploading profile image
# test uploading link thumbnail
# Visitor side
# compare output for visitor side API response (giving profile link as url) with getalldetails/
# Check if response header has cookie (key name: "linktree_visitor")
# for tiny url as query parameter, response status code should be 307
