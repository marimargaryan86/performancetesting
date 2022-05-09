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
  import { writable } from "svelte/store";
  import { checkboxGroup } from "$lib/checkbox-group";
  import { onMount } from "svelte";
  import Checkbox from "$lib/components/ui/checkbox.svelte";
  import { flip } from "svelte/animate";
  import EditButton from "$lib/components/buttons/edit-button.svelte";
  import DeleteButton from "$lib/components/buttons/delete-button.svelte";

  export let searchData: PlaceSearchData;
  let _places: CuratedPlaceModel[] = [];
  export { _places as places };
  export let selectedPlaceIds: string[] = [];
  export let excludedPlaceIds: string[] = [];

  let spinnerVisible = true;

  const pageLimit = 15;
  const transitionTimeMs = 150;
  const placeIds = writable<string[]>([]);
  const { items: places, depleted, pending, infiniteScroll, reset } = create(load, pageLimit);
  const { allChecked, group, multiSelect, toggleAll, unsubscriber } = checkboxGroup(placeIds);

  $: $placeIds = $places
    .filter((place) => excludedPlaceIds.indexOf(place.id) === -1)
    .map((place) => place.id);
  $: selectedPlaceIds = $group;
  $: _places = $places;
  $: searchDataJson = JSON.stringify(searchData);
  $: {
    // Reset places when search data changes.
    searchDataJson;
    reset();
    $group = [];
  }

  async function load(pageOffset: number, pageLimit: number): Promise<CuratedPlaceModel[]> {
    try {
      return await dependencies.placeService.findCurated(searchData, pageOffset, pageLimit);
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
        dependencies.placeService.deleteCurated(place.id);
        excludedPlaceIds = [...excludedPlaceIds, place.id];
        selectedPlaceIds = selectedPlaceIds.filter((placeId) => placeId !== place.id);
      },
    });
  }

  onMount(() => unsubscriber);
</script>

<section class="curated-place-result" use:infiniteScroll={{ threshold: 300 }}>
  {#if !spinnerVisible && $places.length}
    <Table
      on:outroend={() => (spinnerVisible = $pending)}
      stickyHeader
      transition={{ func: fade, params: { duration: transitionTimeMs } }}
    >
      <tr slot="head">
        <td class="select">
          <Checkbox
            checked={$allChecked}
            on:input={toggleAll}
            title="{$allChecked ? 'Deselect' : 'Select'} all"
          />
        </td>
        <td>ID</td>
        <td>Name</td>
        <td>Place count</td>
        <td>Coordinates</td>
        <td>Country code</td>
        <td>Time zone</td>
        <td>Source ref.</td>
        <td>Modified</td>
        <td />
      </tr>

      <svelte:fragment slot="body">
        {#each $places.filter((place) => excludedPlaceIds.indexOf(place.id) === -1) as place, idx (place.id)}
          <tr
            in:fade={{ duration: 150, delay: (idx % pageLimit) * 15 }}
            animate:flip={{ duration: 250 }}
          >
            <td class="select">
              <Checkbox value={place.id} bind:group={$group} on:input={() => multiSelect(idx)} />
            </td>
            <td>{place.id.substring(0, 8)}...</td>
            <td>{place.name}</td>
            <td>{place.mergedPlaces.length}</td>
            <td>{place.coordinates.latitude}°, {place.coordinates.longitude}°</td>
            <td>{place.countryCode}</td>
            <td>{place.timeZone}</td>
            <td>{place.sourceRef.substring(0, 8)}...</td>
            <td>{place.updatedAt.toLocaleDateString(...utils.fullDateTime)}</td>
            <td class="actions">
              <EditButton
                tabindex={-1}
                on:click={(e) => {
                  e.stopPropagation();
                  edit(place);
                }}
                title="Edit"
              />

              <DeleteButton
                tabindex={-1}
                on:click={(e) => {
                  e.stopPropagation();
                  del(place);
                }}
                title="Delete"
              />
            </td>
          </tr>
        {/each}
      </svelte:fragment>
    </Table>
  {:else if !spinnerVisible && $depleted && !$places.length}
    <div
      class="empty"
      transition:fade|local={{ duration: transitionTimeMs }}
      on:outroend={() => (spinnerVisible = $pending)}
    >
      <DocumentNotFoundIcon />
      <span>No curated places found, try broadening your search</span>
    </div>
  {/if}

  {#if $pending && (spinnerVisible || $places.length)}
    <div
      class="pending"
      transition:conditional|local={{
        params: { duration: transitionTimeMs },
        transition: $places.length ? slide : fade,
      }}
      on:outroend={() => (spinnerVisible = $pending)}
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
