import json
def create_profileDetail(client):
	data={
	"profile": {
		"profile_link": "testlink",
		"profile_name": "testprofile",
		"username": "testuser",
		"profile_bio": "This is where user can put any description they like"
	}
}
	response = client.post("/savedetails/",data=json.dumps(data), params={"username": "testuser"})
	assert response.json()["message"] == "Profile details saved"
	assert response.status_code == 201
def create_link(client):
	create_profileDetail(client)
	data1 = {"parameter": {"link_name": "My Musfncjic123","link_url": "https://www.youtube.com/","link_enable": True, "profile_id": 1}}
	response = client.post("/link/",data=json.dumps(data1))
	# assert response.json()["message"] == "Link 2 created"
	assert response.status_code == 201

def get_user_by_profile_link(client):
	create_link(client)
	response = client.get(
		"/testlink/"
	)
	assert response.status_code == 200
	# user variable in link
	short_link = response.json()["data"]["link"][0]["link_tiny"]
	# assert response.json() == short_link
	response1 = client.get(f"/{short_link}", allow_redirects=False)
	assert response1.status_code == 307


def test_user_profile(client):
	get_user_by_profile_link(client)
