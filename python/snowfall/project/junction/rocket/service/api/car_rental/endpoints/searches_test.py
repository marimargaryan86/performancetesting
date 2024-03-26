import httpx

from snowfall.project.junction.rocket import fixtures


class TestListSearchResults(object):
    async def test_list_search_results_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/searches/{searchId}/results".format(
                searchId=fixtures.SEARCHES[0],
            ),
        )

        assert response.status_code == 200
        results = response.json()
        assert len(results["data"]) == 1
