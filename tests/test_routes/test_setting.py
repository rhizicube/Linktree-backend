import json
def create_setting(client):
	data = {
  "parameter": {
	"profile_social": {},
	"profile": 1
  }
}
	response = client.post("/setting/",data=json.dumps(data))
	assert response.status_code == 201
	assert response.json()["message"] == "Setting 1 created"

def create_setting_invalid(client):
	response = client.post(
		"/setting/",
		json={"parameter": {"profile_social": {}}}
	)
	print(response.json())
	assert response.status_code == 422

def get_settings(client):
	response = client.get(
		"/setting/"
	)
	assert response.status_code == 200

def get_setting_by_profile(client):
	response = client.get(
		"/setting/",
		params={"profile_id": 1}
	)
	assert response.status_code == 200

def get_setting_by_profile_invalid(client):
	response = client.get(
		"/api/settings/setting/",
		params={"profile_id": 10000}
	)
	assert response.status_code == 404

def get_setting_by_id(client):
	response = client.get(
		"/setting/",
		params={"setting_id": 1}
	)
	assert response.status_code == 200

def get_setting_by_id_invalid(client):
	response = client.get(
		"/api/settings/setting/",
		params={"setting_id": 101}
	)
	assert response.status_code == 404

def update_setting(client):
	data = {
  "parameter": {
	"profile_social": {}
  }
}
	response = client.put("/setting/",json=data, params={"id": 1})
	assert response.status_code == 200

def update_setting_invalid(client):
	response = client.put(
		"/setting/",
		json={"parameter": {"profile_social": {"ab":"cd"}}},
		params={"id": 10000}
	)
	assert response.status_code == 404

def delete_setting(client):
	response = client.delete(
		"/setting/",
		params={"id": 1}
	)
	assert response.status_code == 200

def delete_setting_invalid(client):
	response = client.delete(
		"/setting/",
		params={"id": 10000}
	)
	assert response.status_code == 404

def test_setting(client):
	create_setting(client)
	create_setting_invalid(client)
	get_settings(client)
	get_setting_by_profile(client)
	get_setting_by_profile_invalid(client)
	get_setting_by_id(client)
	get_setting_by_id_invalid(client)
	update_setting(client)
	update_setting_invalid(client)
	delete_setting(client)
	delete_setting_invalid(client)