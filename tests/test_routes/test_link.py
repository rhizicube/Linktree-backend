import json

def create_profile(client):
	data = {"parameter": {"profile_link": "testtest", "username": "test0123", "profile_name": "Test User12", "profile_bio": "Test user's bio"}}
	response = client.post("/profile/", data=json.dumps(data))
	assert response.status_code == 201
	assert response.json()["message"] == "Profile 2 created"
def create_link(client):
	data = {"parameter": {"profile_link": "testtest", "username": "test0123", "profile_name": "Test User12", "profile_bio": "Test user's bio"}}
	response1 = client.post("/profile/", data=json.dumps(data))
	profile_id = response1.json()["message"][8]
	data1 = {"parameter": {"link_name": "My Mus,fncjic123","link_url": "https://www.smmhdfbule.com/user0123/","link_enable": True, "profile_id": profile_id}}
	response = client.post("/link/",data=json.dumps(data1))
	assert response.json()["message"] == "Link 1 created"
	assert response.status_code == 201

def create_link_invalid(client):
	response = client.post(
		"/link/",
		json={"parameter": {"link_name": "link1","link_url": "link1","link_enable": True}}
	)
	assert response.status_code == 422

def get_links(client):
	response = client.get(
		"/link/"
	)
	assert response.status_code == 200

def get_link_by_id(client):
	response = client.get(
		"/link/",
		params={"link": 1}
	)
	assert response.status_code == 200

def get_link_by_id_invalid(client):
	response = client.get(
		"/link/",
		params={"id": 100}
	)
	assert response.status_code == 404

def get_link_by_profile(client):
	response = client.get(
		"/link/",
		params={"profile": 1}
	)
	assert response.status_code == 200

def get_link_by_profile_invalid(client):
	response = client.get(
		"/api/links/link/",
		params={"profile": 10000}
	)
	assert response.status_code == 404

def update_link(client):
	data = {"parameter": {"link_name": "My Mus,fncjic123","link_url": "https://www.smmhdfbule.com/user0123/","link_enable": True}}
	response = client.put("/link/",data=json.dumps(data), params={"id": 1})
	assert response.status_code == 200

def update_link_invalid(client):
	data = {"parameter": {"link_name": "My Mus,fncjic123","link_url": "https://www.smmhdfbule.com/user0123/","link_enable": True}}
	response = client.put("/api/links/link/",data=json.dumps(data), params={"link": 100})
	assert response.status_code == 404

def delete_link(client):
	response = client.delete(
		"/link/",
		params={"id": 1}
	)
	assert response.status_code == 200

def delete_link_invalid(client):
	response = client.delete(
		"/link/",
		params={"id": 100}
	)
	assert response.status_code == 404

def test_link(client):
	create_link(client)
	create_link_invalid(client)
	get_links(client)
	get_link_by_id(client)
	get_link_by_id_invalid(client)
	get_link_by_profile(client)
	get_link_by_profile_invalid(client)
	update_link(client)
	update_link_invalid(client)
	delete_link(client)
	delete_link_invalid(client)