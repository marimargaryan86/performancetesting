<script lang="ts" context="module">
  /* TODO: While merging, show which curated places will be removed. */
  const countryCodes = ["SE", "DK", "NO", "UK"];
  const timeZones = ["Sweden/Europe", "Seoul/Asia", "Sydney/Australia", "New York/Americ"];
</script>

<script lang="ts">
  import CloseButton from "$lib/components/buttons/close-button.svelte";
  import ConfirmDialogue from "$lib/components/windows/confirm-dialogue.svelte";
  import { showDialogue } from "$lib/components/overlay.svelte";
  import Button from "$lib/components/ui/button.svelte";
  import CoordinatesInput from "$lib/components/ui/coordinates-input.svelte";
  import SelectInput from "$lib/components/ui/select-input.svelte";
  import TextInput from "$lib/components/ui/text-input.svelte";
  import dependencies from "$lib/dependencies";
  import EditDocumentIcon from "$lib/icons/edit-document-icon.svelte";
  import NewDocumentIcon from "$lib/icons/new-document-icon.svelte";
  import SaveIcon from "$lib/icons/save-icon.svelte";
  import type { CuratedPlaceModel, PlaceModel } from "$lib/models/place";
  import { curatedPlaceStore } from "$lib/stores";
  import { createEventDispatcher, onMount } from "svelte";
  import SelectedPlaces from "./selected-places.svelte";
  import MergeDocumentsIcon from "$lib/icons/merge-documents-icon.svelte";

  export let places: PlaceModel[] = [];

  let pending = false;
  let curatedPlace_: Partial<CuratedPlaceModel>;
  let prevCuratedPlace = JSON.stringify(curatedPlace_);

  const dispatch = createEventDispatcher<{ save: CuratedPlaceModel; cancel: void }>();

  let { id, sourceRef, name, countryCode, timeZone, mergedPlaces } = $curatedPlaceStore ?? {};
  let latitude = $curatedPlaceStore?.coordinates.latitude;
  let longitude = $curatedPlaceStore?.coordinates.longitude;
  let dirty = $curatedPlaceStore ? false : !!places.length;
  let mode: "edit" | "merge" | "new";
  places = mergedPlaces ? [...mergedPlaces] : places;

  $: coordinates = !isNaN(latitude) && !isNaN(longitude) ? { latitude, longitude } : undefined;
  $: curatedPlace_ = {
    name,
    coordinates,
    countryCode,
    id,
    mergedPlaces: places,
    sourceRef,
    timeZone,
  };
  $: if (!$curatedPlaceStore) {
    mode = "new";
  } else if ($curatedPlaceStore.removeExisting?.length) {
    mode = "merge";
  } else {
    mode = "edit";
  }
  $: nextCuratedPlace = JSON.stringify(curatedPlace_);

  $: if (prevCuratedPlace !== nextCuratedPlace) {
    dirty = dirty || prevCuratedPlace !== undefined;
    prevCuratedPlace = nextCuratedPlace;
  }

  $: if (places.length) {
    // Set default values when places are being added unless the values have already been tampered with.
    const placeData = places[0];
    name = name === undefined ? placeData.name : name;
    countryCode = countryCode === undefined ? placeData.countryCode : countryCode;
    timeZone = timeZone === undefined ? placeData.timeZone : timeZone;
    latitude = isNaN(latitude) ? placeData.coordinates.latitude : latitude;
    longitude = isNaN(longitude) ? placeData.coordinates.longitude : longitude;
  }

  async function save(): Promise<void> {
    if (!dirty) {
      dispatch("cancel");
      return;
    }

    if (pending) {
      return;
    }

    try {
      pending = true;

      dispatch("save", await dependencies.placeService.putCuratedPlace({ ...curatedPlace_ }));
    } catch {
      // TODO: Handle errors.
    } finally {
      pending = false;
    }
  }

  function cancel(): void {
    if (dirty) {
      showDialogue(ConfirmDialogue, {
        title: "Discard changes",
        message: "Are you sure you want to discard your changes?",
        onConfirm: () => dispatch("cancel"),
      });

      return;
    }

    dispatch("cancel");
  }

  onMount(() => () => ($curatedPlaceStore = undefined));
</script>

<div class="curated-place-dialogue">
  <h2>
    {#if mode === "edit"}
      <EditDocumentIcon />
    {:else if mode === "new"}
      <NewDocumentIcon />
    {:else}
      <MergeDocumentsIcon />
    {/if}

    <span>
      {#if mode === "edit"}
        Edit
      {:else if mode === "new"}
        Create
      {:else}
        Merge
      {/if}

      curated place{mode === "merge" ? "s" : ""}{dirty ? "*" : ""}
    </span>

    <CloseButton on:click={cancel} />
  </h2>

  <form on:submit|preventDefault={save}>
    <TextInput label="Name" bind:value={name} />

    <CoordinatesInput bind:latitude bind:longitude />

    <SelectInput label="Country code" items={countryCodes} bind:value={countryCode} />

    <SelectInput label="Time zone" items={timeZones} bind:value={timeZone} />

    <SelectedPlaces bind:places />

    <Button submit>
      <SaveIcon />

      <span>Save</span>
    </Button>
  </form>
</div>

<style>
  .curated-place-dialogue {
    background-color: var(--color-gray-light);
    padding: 8px;
  }

  h2 {
    user-select: none;
    display: grid;
    grid-template-columns: max-content 1fr max-content;
    gap: 4px;
    font-size: 16px;
    margin-bottom: 8px;
    color: var(--color-teal-dark);
    fill: var(--color-teal-dark);
    align-items: center;
    justify-content: space-between;
  }

  form {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
  }

  form > :global(.selected-places) {
    max-height: 400px;
  }
</style>
