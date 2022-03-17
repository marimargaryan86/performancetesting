from starlette import status, testclient

from snowfall import fixtures


class TestSegments(object):
    def test_unknown_segment_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/segments/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_segment_is_found(self, client: testclient.TestClient) -> None:
        response = client.get("/segments/{id}".format(id=fixtures.SEGMENTS[0]))
        assert response.status_code == status.HTTP_200_OK
