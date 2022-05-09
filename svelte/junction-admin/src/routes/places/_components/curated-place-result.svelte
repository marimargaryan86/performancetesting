<script lang="ts">
  import { goto } from "$app/navigation";
  import ConfirmDialogue from "$lib/components/windows/confirm-dialogue.svelte";
  import { showDialogue } from "$lib/components/overlay.svelte";
  import Table from "$lib/components/ui/table.svelte";

  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import create from "$lib/infinite-scroll";
  import type { CuratedPlaceModel, PlaceSearchData } from "$lib/models/place";
  import routeConfig from "$lib/route-config";
  import { curatedPlaceStore } from "$lib/stores";
  import { conditional } from "$lib/transitions";
  import utils from "$lib/utils";
  import { fade, slide } from "svelte/transition";

  export let searchData: PlaceSearchData;
  export let places: CuratedPlaceModel[] = [];
  export let selectedPlaceIds: string[] = [];
  export let excludedPlaceIds: string[] = [];

  let spinnerVisible = true;

  const pageLimit = 15;
  const transitionTimeMs = 150;
  const { store, infiniteScroll, reset } = create(load, pageLimit);

  $: places = $store.items;
  $: searchDataJson = JSON.stringify(searchData);
  $: {
    // Reset places when search data changes.
    searchDataJson;
    reset();
    selectedPlaceIds = [];
  }

  async function load(pageOffset: number, pageLimit: number): Promise<CuratedPlaceModel[]> {
    try {
      return await dependencies.placeService.findCuratedPlaces(searchData, pageOffset, pageLimit);
    } catch {
      return [];
    }
  }

  function edit(place: CuratedPlaceModel): void {
    $curatedPlaceStore = place;

    goto(routeConfig.places.root);
  }

  function del(place: CuratedPlaceModel): void {
    showDialogue(ConfirmDialogue, {
      title: "Delete curated place",
      message: "Are you sure you want to delete this curated place?",
      onConfirm: () => {
        dependencies.placeService.deleteCuratedPlace(place.id);
        excludedPlaceIds = [...excludedPlaceIds, place.id];
        selectedPlaceIds = selectedPlaceIds.filter((placeId) => placeId !== place.id);
      },
    });
  }
</script>

<section class="curated-place-result" use:infiniteScroll={{ threshold: 300 }}>
  {#if !spinnerVisible}
    {#if $store.items.length}
      <Table
        headers={[
          { title: "ID" },
          { title: "Name" },
          { title: "Place count" },
          { title: "Coordinates" },
          { title: "Country code" },
          { title: "Time zone" },
          { title: "Source ref." },
          { title: "Last modified" },
        ]}
        selectable
        bind:selectedIds={selectedPlaceIds}
        actions={{ edit, delete: del }}
        {pageLimit}
        values={$store.items.filter((place) => excludedPlaceIds.indexOf(place.id) === -1)}
        formatter={(place) => [
          `${place.id.substring(0, 8)}...`,
          place.name,
          place.mergedPlaces.length,
          `${place.coordinates.latitude}°, ${place.coordinates.longitude}°`,
          place.countryCode,
          place.timeZone,
          `${place.sourceRef.substring(0, 8)}...`,
          place.updatedAt.toLocaleDateString("sv-SE", utils.fullDateTime),
        ]}
        on:outroend={() => (spinnerVisible = $store.pending)}
      />
    {:else if $store.depleted && !$store.items.length}
      <div
        class="empty"
        transition:fade|local={{ duration: transitionTimeMs }}
        on:outroend={() => (spinnerVisible = $store.pending)}
      >
        <DocumentNotFoundIcon />
        <span>No curated places found, try broadening your search</span>
      </div>
    {/if}
  {/if}

  {#if $store.pending && (spinnerVisible || $store.items.length)}
    <div
      class="pending"
      transition:conditional|local={{
        params: { duration: transitionTimeMs },
        transition: $store.items.length ? slide : fade,
      }}
      on:outroend={() => (spinnerVisible = $store.pending)}
    >
      <SpinnerIcon />
    </div>
  {/if}
</section>

<style>
  .curated-place-result {
    padding: 0 8px 8px;
    overflow-y: auto;
  }

  .pending,
  .empty {
    text-align: center;
    padding: 8px;
    fill: var(--color-teal);
    user-select: none;
  }

  .empty {
    fill: var(--color-black);
    font-size: 12px;
  }

  .pending > :global(*),
  .empty > :global(*) {
    vertical-align: middle;
  }

  .curated-place-result > :global(.table) {
    width: 100%;
  }
</style>
