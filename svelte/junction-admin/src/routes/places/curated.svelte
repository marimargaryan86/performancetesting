<script lang="ts">
  import type { CuratedPlaceModel, PlaceSearchData } from "$lib/models/place";
  import PlaceSearch from "./_components/place-search.svelte";
  import CuratedPlaceResult from "./_components/curated-place-result.svelte";
  import Button from "$lib/components/ui/button.svelte";
  import RemoveDocumentIcon from "$lib/icons/remove-document-icon.svelte";
  import dependencies from "$lib/dependencies";
  import { showDialogue } from "$lib/components/overlay.svelte";
  import ConfirmDialogue from "$lib/components/windows/confirm-dialogue.svelte";
  import routeConfig from "$lib/route-config";
  import { curatedPlaceStore } from "$lib/stores";
  import { goto } from "$app/navigation";
  import MergeDocumentsIcon from "$lib/icons/merge-documents-icon.svelte";

  let searchData: PlaceSearchData;
  let selectedPlaceIds: string[] = [];
  let excludedPlaceIds: string[] = [];
  let places: CuratedPlaceModel[];

  $: latitude = searchData?.coordinates.latitude;
  $: longitude = searchData?.coordinates.longitude;
  $: name = searchData?.name;
  $: proximity = searchData?.proximity;

  async function deleteSelected_(): Promise<void> {
    selectedPlaceIds.map((placeId) => dependencies.placeService.deleteCuratedPlace(placeId));

    excludedPlaceIds = [...selectedPlaceIds, ...excludedPlaceIds];
    selectedPlaceIds = [];

    // TODO: Check so that no tasks throw.
  }

  function deleteSelected(): void {
    showDialogue(ConfirmDialogue, {
      title: "Delete curated places",
      message: "Are you sure you want to delete the selected places?",
      onConfirm: deleteSelected_,
    });
  }

  function mergeSelected(): void {
    $curatedPlaceStore = {
      ...places.find((place) => place.id === selectedPlaceIds[0]),
      mergedPlaces: Array.from(
        new Set(
          places
            .filter((place) => selectedPlaceIds.indexOf(place.id) !== -1)
            .reduce((prev, curr) => [...prev, ...curr.mergedPlaces], []),
        ),
      ),
      removeExisting: [...selectedPlaceIds],
    };

    goto(routeConfig.places.root);
  }
</script>

<svelte:head>
  <title>Place management | Curated places</title>
</svelte:head>

<section class="curated-places">
  <PlaceSearch
    on:search={(e) => (searchData = e.detail)}
    {latitude}
    {longitude}
    {name}
    {proximity}
  />

  <div class="main">
    <div class="actions">
      <Button type="delete" on:click={deleteSelected} disabled={!selectedPlaceIds.length}>
        <RemoveDocumentIcon />
        <span>Delete selected</span>
      </Button>

      <Button on:click={mergeSelected} disabled={selectedPlaceIds.length < 2}>
        <MergeDocumentsIcon />
        <span>Merge selected</span>
      </Button>
    </div>

    <CuratedPlaceResult {searchData} bind:selectedPlaceIds bind:excludedPlaceIds bind:places />
  </div>
</section>

<style>
  .curated-places {
    display: grid;
    height: 100%;
    grid-template-columns: 280px 1fr;
  }

  .main {
    display: grid;
    grid-template-rows: 64px 1fr;
    height: 100%;
    position: relative;
  }

  .actions {
    display: flex;
    padding: 4px;
  }

  .actions > :global(button) {
    padding: 0 24px;
    margin: 4px;
  }

  .main > :global(.curated-place-result) {
    height: calc(100% - 64px);
    top: 64px;
    width: 100%;
    position: absolute;
  }
</style>
