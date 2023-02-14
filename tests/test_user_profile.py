import json
def test_get_user(client):
    response = client.get(
        "/api/users/?url=sjbsdj"
    )
    assert response.status_code == 404
 