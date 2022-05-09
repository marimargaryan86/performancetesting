<script lang="ts">
  import Button from "$lib/components/ui/button.svelte";
  import Checkbox from "$lib/components/ui/checkbox.svelte";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import RemoveIcon from "$lib/icons/remove-icon.svelte";
  import type { PlaceModel } from "$lib/models/place";
  import utils from "$lib/utils";
  import { onMount } from "svelte";
  import { flip } from "svelte/animate";
  import { fade } from "svelte/transition";

  export let places: PlaceModel[] = [];

  let selectedPlaceIds: string[] = [];
  let flashingPlaceIds: string[] = [];
  let lastSelectedIndex: number = undefined;
  let shiftDown = false;

  $: places, (lastSelectedIndex = undefined);
  $: allSelected = places.reduce(
    (prev, curr) => prev && selectedPlaceIds.indexOf(curr.id) !== -1,
    true,
  );

  function selectAll(e: InputEvent): void {
    selectedPlaceIds = (e.currentTarget as HTMLInputElement).checked
      ? places.map((value) => value.id)
      : [];
  }

  function remove(): void {
    places = places.filter((place) => selectedPlaceIds.indexOf(place.id) === -1);
    selectedPlaceIds = [];
  }

  async function flashPlace(place: PlaceModel): Promise<void> {
    if (flashingPlaceIds.indexOf(place.id) !== -1) {
      return;
    }

    flashingPlaceIds = [place.id, ...flashingPlaceIds];
    await utils.sleep(1300);
    flashingPlaceIds = flashingPlaceIds.filter((placeId) => placeId !== place.id);
  }

  function multiSelect(index: number): void {
    if (isNaN(lastSelectedIndex)) {
      lastSelectedIndex = index;
    }

    if (!shiftDown) {
      lastSelectedIndex = index;

      return;
    }

    const mode = selectedPlaceIds.indexOf(places[index].id) === -1 ? "select" : "deselect";
    const start = Math.min(index, lastSelectedIndex);
    const end = Math.max(index, lastSelectedIndex) + 1;
    const nextSelectedPlaceIds = places.slice(start, end).map((value) => value.id);

    if (mode === "select") {
      selectedPlaceIds = Array.from(new Set([...selectedPlaceIds, ...nextSelectedPlaceIds]));
    } else {
      selectedPlaceIds = selectedPlaceIds.filter(
        (placeId) => nextSelectedPlaceIds.indexOf(placeId) === -1,
      );
    }
  }

  onMount(() => {
    function toggle(e: KeyboardEvent) {
      shiftDown = e.shiftKey || false;
    }

    window.addEventListener("focus", toggle);
    window.addEventListener("keydown", toggle);
    window.addEventListener("keyup", toggle);

    return () => {
      window.removeEventListener("focus", toggle);
      window.removeEventListener("keydown", toggle);
      window.removeEventListener("keyup", toggle);
    };
  });
</script>

<div class="selected-places">
  {#if !places.length}
    <div class="empty">
      <DocumentNotFoundIcon />
      <span>No places added</span>
    </div>
  {:else}
    <ol class="places">
      <li class="remove">
        <Button type="delete" on:click={remove} disabled={!selectedPlaceIds.length}>
          <RemoveIcon />
          Remove selected
        </Button>
      </li>

      <li class="header">
        <Checkbox checked={allSelected} on:input={selectAll} label="Selected places" />
      </li>

      {#each places as place, idx (place.id)}
        <li
          class="place"
          animate:flip={{ duration: 250 }}
          in:fade={{ duration: 0 }}
          on:introend={() => flashPlace(place)}
          class:alerting={flashingPlaceIds.indexOf(place.id) !== -1}
        >
          <div>
            <Checkbox
              value={place.id}
              bind:group={selectedPlaceIds}
              on:input={() => multiSelect(idx)}
            />
          </div>

          <div class="info">
            <strong>{place.name}</strong>
            <span>{place.id}</span>
          </div>
        </li>
      {/each}
    </ol>
  {/if}
</div>

<style>
  .selected-places {
    background-color: var(--color-white);
    border-radius: 4px;
    border: 1px solid var(--color-gray);
    overflow-y: auto;
    user-select: none;
  }

  .empty {
    font-size: 12px;
    padding: 8px;
    text-align: center;
    color: var(--color-black);
    fill: var(--color-black);
  }

  .empty > :global(svg),
  .empty > span {
    vertical-align: middle;
  }

  .empty > :global(svg) {
    margin-right: 4px;
  }

  .places {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 0 0 4px;
  }

  .places :global(button) {
    width: 100%;
  }

  .remove {
    position: sticky;
    top: 0;
    left: 0;
    padding: 4px;
    background-color: var(--color-white);
    box-shadow: var(--drop-shadow);
  }

  .header {
    padding: 4px 8px;
    font-size: 12px;
    align-items: center;
    color: var(--color-teal-dark);
  }

  .place {
    padding: 4px 8px;
    display: grid;
    gap: 8px;
    grid-template-columns: max-content 1fr;
    background-color: var(--color-white);
    align-items: center;
  }

  .place.alerting {
    animation: alert 400ms linear 3;
  }

  .info {
    display: grid;
    grid-template-columns: 1fr;
    gap: 4px;
  }

  .info > strong {
    font-size: 12px;
  }

  .info > span {
    color: var(--color-gray-dark);
    font-size: 10px;
  }

  @keyframes alert {
    0% {
      background-color: rgba(210, 234, 228, 0.2);
    }
    50% {
      background-color: rgb(210, 234, 228);
    }
    100% {
      background-color: var(--color-white);
    }
  }
</style>
