
def test_admin_route_without_token(client):
    response = client.get("/auth/admin")

    assert response.status_code == 401


def test_recruiter_route_without_token(client):
    response = client.get("/auth/recruiter")

    assert response.status_code == 401


def test_job_seeker_route_without_token(client):
    response = client.get("/auth/job-seeker")

    assert response.status_code == 401

