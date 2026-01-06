
def test_create_ride_unauthorized(client):
    response = client.post("/api/v1/rides/request", json={})
    assert response.status_code in [401, 403]


