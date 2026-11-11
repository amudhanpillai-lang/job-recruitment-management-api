
def test_resume_upload_without_authentication(client):
    response = client.post(
        "/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                b"%PDF-1.4 test resume content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 401


def test_get_resume_without_authentication(client):
    response = client.get("/resumes/me")

    assert response.status_code == 401


def test_download_resume_without_authentication(client):
    response = client.get("/resumes/download")

    assert response.status_code == 401


def test_delete_resume_without_authentication(client):
    response = client.delete("/resumes/me")

    assert response.status_code == 401
