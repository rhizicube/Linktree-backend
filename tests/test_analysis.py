import json
import datetime
from datetime import date
from sqlalchemy.sql import func
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
def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} is not serializable')

def create_view(client):
    create_profileDetail(client)
    d = datetime.datetime.strptime("2023-01-28T07:43:50.340390", "%Y-%m-%dT%H:%M:%S.%f")
    data = {
    "parameter": {
    "session_id": "123ABC",
    "device_name": "device",
    "view_count": 10,
    "profiles": 1,
    "view_sampled_timestamp": "2023-02-16T10:45:44.025Z"
  }
}
    response = client.post("/views/", data=json.dumps(data))
    assert response.status_code == 201
    assert response.json()["message"] == "View 1 created"

def get_analysis_with_date(client):
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
    data = {
    "parameter": {
    "session_id": "123ABC",
    "device_name": "device",
    "view_count": 10,
    "profiles": 1,
    "view_sampled_timestamp": "2023-02-16T10:45:44.025Z"
  }
}
    response = client.post("/views/", data=json.dumps(data))
    assert response.status_code == 201
    # assert response.json()["message"] == "View 1 created"
    data = {
    "parameter": {
    "session_id": "123ABC",
    "device_name": "device",
    "view_count": 20,
    "profiles": 1,
    "view_sampled_timestamp": "2023-02-01T10:45:44.025Z"
  }
}
    response = client.post("/views/", data=json.dumps(data))
    # create_view(client)
    response = client.get(
        "/analytics/getactivitycount/",
        params={"username": "testuser", "start": "2023-01-28T06:31:52.580654", "end": "2023-02-28T06:31:52.580654", "freq": "daily"}
    )
    # assert response.json() == {}
    assert response.status_code == 200


def get_metrics(client):
    create_profileDetail(client)
    response = client.get("/analytics/getmetrics/", params={"username": "testuser"})
    assert response.status_code == 200

def test_analysis(client):
    get_metrics(client)
    get_analysis_with_date(client)
