from snowfall.project.junction.extensions.service.mobile_api import repository


async def test_match_with_dash(
    places_repository: repository.PlacesRepository,
) -> None:
    documents = await places_repository.match("Aachen-Rothe")
    contains_document = False
    async for document in documents:
        if getattr(document, "name", None) == "Aachen-Rothe Erde":
            contains_document = True
            break
    assert contains_document
