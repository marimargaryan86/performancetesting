import http

from starlette import status, testclient


def test_not_found_content_type(client: testclient.TestClient) -> None:
    response = client.get("/not_found")
    assert response.headers["content-type"] == "application/vnd.api+json"


def test_not_found_status_code(client: testclient.TestClient) -> None:
    response = client.get("/not_found")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_not_found_format(client: testclient.TestClient) -> None:
    response = client.get("/not_found")
    status_code = http.HTTPStatus(status.HTTP_404_NOT_FOUND)

    for error in response.json()["errors"]:
        assert error["status"] == str(status.HTTP_404_NOT_FOUND)
        assert error["title"] == status_code.phrase
        assert error["detail"] == status_code.description
