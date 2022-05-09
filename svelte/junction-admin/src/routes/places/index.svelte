<script lang="ts">
  import type { CuratedPlaceModel, PlaceModel, PlaceSearchData } from "$lib/models/place";
  import { slide } from "$lib/transitions";
  import PlaceSearch from "./_components/place-search.svelte";
  import CuratedPlaceDialogue from "./_components/curated-place-dialogue.svelte";
  import PlaceResult from "./_components/place-result.svelte";
  import Button from "$lib/components/ui/button.svelte";
  import AddIcon from "$lib/icons/add-icon.svelte";
  import NewDocumentIcon from "$lib/icons/new-document-icon.svelte";
  import { curatedPlaceStore } from "$lib/stores";

  let expanded = false;
  let searchData: PlaceSearchData;
  let places: PlaceModel[] = [];
  let selectedPlaceIds: string[] = [];
  let selectedPlaces: PlaceModel[] = [];

  $: expanded = expanded || !!$curatedPlaceStore || !!selectedPlaces.length;
  $: name = searchData?.name;
  $: longitude = searchData?.coordinates.longitude;
  $: latitude = searchData?.coordinates.latitude;
  $: proximity = searchData?.proximity;

  $: {
    if (!searchData && $curatedPlaceStore) {
      searchData = {
        name: $curatedPlaceStore.name,
        coordinates: {
          ...$curatedPlaceStore.coordinates,
        },
        proximity: 1000,
      };
    }
  }

  function closeDialogue(): void {
    $curatedPlaceStore = undefined;
    selectedPlaces = [];
    expanded = false;
  }

  async function save(curatedPlace: CuratedPlaceModel): Promise<void> {
    console.log(curatedPlace);

    closeDialogue();
  }

  function addSelected(): void {
    selectedPlaces = Array.from(
      new Set([
        ...places.filter((place) => selectedPlaceIds.indexOf(place.id) !== -1),
        ...selectedPlaces,
      ]),
    );
    selectedPlaceIds = [];
  }
</script>

<svelte:head>
  <title>Place management</title>
</svelte:head>

<section class="places">
  <PlaceSearch
    on:search={(e) => (searchData = e.detail)}
    {name}
    {longitude}
    {latitude}
    {proximity}
  />

  <div class="main">
    <div class="actions">
      {#if expanded}
        <Button on:click={addSelected} disabled={!selectedPlaceIds.length}>
          <AddIcon />
          <span>Add selected</span>
        </Button>
      {:else}
        <Button
          on:click={() => {
            addSelected();
            expanded = true;
          }}
        >
          <NewDocumentIcon />
          <span>New curated place</span>
        </Button>
      {/if}
    </div>

    <PlaceResult
      {searchData}
      bind:selectedPlaceIds
      bind:places
      excludedPlaceIds={selectedPlaces.map((place) => place.id)}
    />
  </div>

  {#if expanded}
    <div class="dialogue" transition:slide|local={{ direction: "horizontal", duration: 250 }}>
      <CuratedPlaceDialogue
        on:save={(e) => save(e.detail)}
        on:cancel={closeDialogue}
        bind:places={selectedPlaces}
      />
    </div>
  {/if}
</section>

<style>
  .places {
    display: grid;
    height: 100%;
    grid-template-columns: 280px 1fr max-content;
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

  .main > :global(.place-result) {
    height: calc(100% - 64px);
    top: 64px;
    width: 100%;
    position: absolute;
  }

  .dialogue {
    box-shadow: var(--drop-shadow);
    height: 100%;
  }

  .dialogue > :global(.curated-place-dialogue) {
    width: 280px;
    height: 100%;
  }
</style>
