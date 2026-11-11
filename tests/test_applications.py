def test_apply_without_authentication(client):
    response = client.post(
        "/applications/",
        json={"job_id": 1, "cover_letter": "I am interested"}
    )

    assert response.status_code == 401


def test_applications_require_authentication(client):
    response = client.get("/applications/my-applications")

    assert response.status_code == 401
