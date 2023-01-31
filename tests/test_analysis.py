import json

def get_analysis_with_both_date(client):
    response = client.get(
        "/analysis/",
        params={"id": 1, "start": "2023-01-28T06:31:52.580654", "end": "2023-01-31T06:31:52.580654"}
    )
    assert response.status_code == 200
    # assert response.json()["message"] == "Success"

def get_analysis_with_start_date(client):
    response = client.get(
        "/analysis/",
        params={"id": 1, "start": "2023-01-28T06:31:52.580654"}
    )
    assert response.status_code == 200
    # assert response.json()["message"] == "Success"

def get_analysis_with_end_date(client):
    response = client.get(
        "/analysis/",
        params={"id": 1, "end": "2023-01-31T06:31:52.580654"}
    )
    assert response.status_code == 200
    # assert response.json()["message"] == "Success"



def get_analysis_without_date(client):
    response = client.get(
        "/analysis/",
        params={"id": 1}
    )
    assert response.status_code == 200
    # assert response.json()["message"] == "Success"

def test_analysis(client):
    get_analysis_with_both_date(client)
    get_analysis_with_start_date(client)
    get_analysis_with_end_date(client)
    get_analysis_without_date(client)



