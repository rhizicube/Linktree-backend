import json
from datetime import datetime as dt


def create_profile(client):
	data = {"parameter": {"profile_link": "test", "username": "test01", "profile_name": "Test User", "profile_bio": "Test user's bio"}}
	response = client.post("/profile/", data=json.dumps(data))
	assert response.status_code == 201
	assert response.json()["message"] == "Profile 1 created"

def create_profile_invalid(client):
	data = {"parameter": {"profile_link": "test"}}
	response = client.post("/profile/", data=json.dumps(data))
	assert response.status_code == 422


def get_profile(client):
	response = client.get("/profile/")
	assert response.status_code == 200

def get_profile_by_id(client):
	response = client.get("/profile/", params={"profile": 1})
	assert response.status_code == 200

def get_profile_by_username(client):
	response = client.get("/profile/", params={"uname": "test01"})
	assert response.status_code == 200

def get_profile_by_username_invalid(client):
	response = client.get("/api/profiles/profile/", params={"uname": "temndcbstuser2"})
	assert response.status_code == 404
	# assert response.json()["message"] == "Profile testuser2 not found"

def get_profile_by_id_invalid(client):
	response = client.get("/profile/", params={"id": 2})
	assert response.status_code == 404
	assert response.json()["message"] == "Profile 2 not found"

def update_profile(client):
	data = {"parameter": {"profile_bio": "Test user's bio changed kjd", "profile_name": "testuser2changed6468", "profile_link": "linkupdated"}}
	response = client.put("/profile/", params={"id": 1}, data=json.dumps(data))
	# assert response.json()["detail"] == "Profile 1 updated"
	assert response.status_code == 200

def update_profile_invalid(client):
	data = {"parameter": {"profile_bio": "Test user's bio", "profile_link": "testuser2"}}
	response = client.put("/api/profiles/profile/", data=json.dumps(data), params={"id": 2})
	assert response.status_code == 404

def delete_profile(client):
	data = {"parameter": {"profile_link": "tesdbt", "username": "test0123456543", "profile_name": "Test User123214", "profile_bio": "Test user's bio12321"}}
	response1 = client.post("/profile/", data=json.dumps(data))
	profile_id = response1.json()["message"][8]
	profile_id = int(profile_id)
	assert profile_id == 2
	response = client.delete("/profile/", params={"id": 2})
	# assert response.json() == "Profile 2 deleted"
	assert response.status_code == 200

def delete_profile_invalid(client):
	response = client.delete("/profile/", params={"id": 100})
	assert response.status_code == 404

def test_profile(client):
	create_profile(client)
	create_profile_invalid(client)
	get_profile(client)
	get_profile_by_id(client)
	get_profile_by_username(client)
	get_profile_by_username_invalid(client)
	get_profile_by_id_invalid(client)
	update_profile(client)
	update_profile_invalid(client)
	delete_profile(client)  # not working
	delete_profile_invalid(client)




