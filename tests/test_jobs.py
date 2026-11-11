from urllib import response
from app.models.user import User

# Helper function to register a user
def register_user(client, name, email, password):
    return client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )


# Helper function to log in and obtain JWT token
def login_user(client, email, password):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    assert response.status_code == 200
    return response.json()["access_token"]


# Test public job listing
def test_get_jobs(client):
    response = client.get("/jobs")

    assert response.status_code == 200


# Test requesting a job that does not exist
def test_get_job_not_found(client):
    response = client.get("/jobs/999999")

    assert response.status_code == 404



def test_recruiter_can_create_job(client, db_session):

    # Register a new user
    registration = register_user(
        client,
        "Recruiter",
        "recruiter@example.com",
        "TestPassword123!"
    )

    assert registration.status_code in [200, 201]

    # Find the user in the test database
    user = db_session.query(User).filter_by(
        email="recruiter@example.com"
    ).first()

    assert user is not None

    # Promote user to recruiter
    user.role = "recruiter"
    db_session.commit()

    # Login as recruiter
    token = login_user(
        client,
        "recruiter@example.com",
        "TestPassword123!"
    )

    # Create a job
    response = client.post(
        "/jobs",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Python Backend Developer",
            "description": "Develop APIs using FastAPI",
            "location": "Remote",
            "company": "Test Company",
            "salary": 80000
        }
    )

    # Display validation error if request fails
    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.json())

    assert response.status_code in [200, 201]


