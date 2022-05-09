<script lang="ts">
  import { checkboxGroup } from "$lib/checkbox-group";
  import Checkbox from "$lib/components/ui/checkbox.svelte";
  import Table from "$lib/components/ui/table.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import create from "$lib/infinite-scroll";
  import type { PlaceModel, PlaceSearchData } from "$lib/models/place";
  import { conditional } from "$lib/transitions";
  import utils from "$lib/utils";
  import { onMount } from "svelte";
  import { flip } from "svelte/animate";
  import { writable } from "svelte/store";
  import { fade, slide } from "svelte/transition";

  export let searchData: PlaceSearchData;
  let _places: PlaceModel[] = [];
  export { _places as places };
  export let selectedPlaceIds: string[] = [];
  export let excludedPlaceIds: string[] = [];

  let spinnerVisible = true;

  const pageLimit = 15;
  const transitionTimeMs = 150;
  const placeIds = writable<string[]>([]);
  const { items: places, pending, depleted, infiniteScroll, reset } = create(load, pageLimit);
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

  async function load(pageOffset: number, pageLimit: number): Promise<PlaceModel[]> {
    try {
      return await dependencies.placeService.find(searchData, pageOffset, pageLimit);
    } catch {
      return [];
    }
  }

  onMount(() => unsubscriber);
</script>

<section class="place-result" use:infiniteScroll={{ threshold: 300 }}>
  {#if !spinnerVisible && $places.length}
    <Table
      stickyHeader
      on:outroend={() => (spinnerVisible = $pending)}
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
        <td>Coordinates</td>
        <td>Country code</td>
        <td>Time zone</td>
        <td>Source ref.</td>
        <td>Modified</td>
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
            <td>{place.coordinates.latitude}°, {place.coordinates.longitude}°</td>
            <td>{place.countryCode}</td>
            <td>{place.timeZone}</td>
            <td>{place.sourceRef.substring(0, 8)}...</td>
            <td>{place.updatedAt.toLocaleDateString(...utils.fullDateTime)}</td>
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
      <span>No places found, try broadening your search</span>
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
  .place-result {
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

  .place-result > :global(.table) {
    width: 100%;
  }
</style>
