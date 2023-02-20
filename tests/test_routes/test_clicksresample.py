import json
def create_click(client):
	data1 = {"parameter": {"profile_link": "testvnbvtest", "username": "test012345", "profile_name": "Test User1234", "profile_bio": "Test user's bio"}}
	response1 = client.post("/profile/", data=json.dumps(data1))
	profile_id = response1.json()["message"][8]
	data2={"parameter": {"session_id": "12321434","device_type": "view1devi3ce","view_count": 20,"profiles": profile_id}}
	response2 = client.post("/views/", data=json.dumps(data2))
	view_id = response2.json()["message"][5]
	view_id = int(view_id)
	data3 = {"parameter": {"link_name": "My Mus,fncjic123","link_url": "https://www.smmhdfbule.com/user0123/","link_enable": True, "profile_id": profile_id}}
	response3 = client.post("/link/", data=json.dumps(data3))
	link_id = response3.json()["message"][5]
	link_id = int(link_id)
	data4 = {
  "parameter": {
	"click_count": 100,
	"view_id": view_id,
	"link_id": link_id
  }
}
	response4 = client.post("/click/",data=json.dumps(data4))
	click_id = response4.json()["message"][6]
	click_id = int(click_id)
	data = {
  "parameter": {
	"click_count": 100,
	"view_id": view_id,
	"link_id": link_id
  }
}
	response = client.post("/click/",data=json.dumps(data))
	assert response.status_code == 201
	assert response.json()["message"] == "Click 2 created"

def create_click_invalid(client):
	response = client.post(
		"/click/",
		json={"parameter": {"click_count": 100,"view_id": 1}}
	)
	print(response.json())
	assert response.status_code == 422

def get_clicks(client):
	response = client.get(
		"/click/"
	)
	assert response.status_code == 200


def get_click_by_id(client):
	response = client.get("/click/", params={"click_id": 1})
	assert response.status_code == 200

def get_click_by_id_invalid(client):
	response = client.get(
		"/click/",
		params={"id": 100}
	)
	assert response.status_code == 404

def get_click_by_view_id(client):
	response = client.get(
		"/clicks/",
		params={"view_id": 1}
	)
	assert response.status_code == 200

def get_click_by_view_id_invalid(client):
	response = client.get(
		"/api/clicks/clicks/",
		params={"view_id": 100}
	)
	assert response.status_code == 404

def get_click_by_link_id(client):
	response = client.get(
		"/clicks/",
		params={"link_id": 1}
	)
	assert response.status_code == 200


def get_click_by_link_id_invalid(client):
	response = client.get(
		"/api/click/clicks/",
		params={"link_id": 100}
	)
	assert response.status_code == 404

def update_click(client):
	
	data = {
  "parameter": {
	"click_count": 100
  }
}
	response = client.put("/api/clicks/click/",data=json.dumps(data), params={"id": 1})
	assert response.status_code == 200
	assert response.json()["message"] == "Click 1 updated"

def update_click_invalid(client):
	response = client.put(
		"/click/",
		json={"parameter": {"click_count": 100,"view_id": 1}}
	)
	print(response.json())
	assert response.status_code == 422

def delete_clicks(client):
	response = client.delete("/click/")
	assert response.status_code == 200
	assert response.json()["message"] == "Clicks deleted"
def delete_click(client):
	response = client.delete("/click/", params={"id": 1})
	assert response.status_code == 200
	assert response.json()["message"] == "Click 1 deleted"

def delete_click_invalid(client):
	response = client.delete(
		"/click/",
		params={"id": 100}
	)
	assert response.status_code == 404

def test_clicksresample(client):
	create_click(client)
	get_clicks(client)
	get_click_by_id(client)
	get_click_by_view_id(client)
	get_click_by_link_id(client)
	# update_click(client)
	# delete_clicks(client)
	create_click_invalid(client)
	get_click_by_id_invalid(client)
	get_click_by_view_id_invalid(client)
	get_click_by_link_id_invalid(client)
	update_click_invalid(client)
	delete_click_invalid(client)
	delete_click(client)

