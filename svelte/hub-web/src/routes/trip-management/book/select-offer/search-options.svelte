<script lang="ts" context="module">
  type SortValue =
    | "price"
    | "fastest"
    | "earliest-departure"
    | "latest-departure"
    | "earliest-arrival"
    | "latest-arrival";
  type SortOption = { label: string; value: SortValue };
  type StopValue = "direct" | "non-stop" | "indirect";
  type TimeSpan = { start: number; end: number };

  export type SearchOptionsData = {
    sortBy: SortValue;
    stops: StopValue[];
    departureSpan: TimeSpan;
    arrivalSpan: TimeSpan;
    duration: number;
    operators: number[];
  };

  const sortValues: SortOption[] = [
    { label: "Lowest price", value: "price" },
    { label: "Fastest", value: "fastest" },
    { label: "Earliest departure", value: "earliest-departure" },
    { label: "Latest departure", value: "latest-departure" },
    { label: "Earliest arrival", value: "earliest-arrival" },
    { label: "Latest arrival", value: "latest-arrival" },
  ];

  const operators = [
    { name: "Provider 1", id: 0 },
    { name: "Provider 2", id: 1 },
    { name: "Provider 3", id: 2 },
  ];

  function formatSortBy(value?: SortOption): string {
    return value?.label ?? "Price";
  }

  function formatTime(minutes: number): string {
    const hours = Math.floor(minutes / 60);
    const minute = minutes % 60;

    return `${hours < 10 ? 0 : ""}${hours}:${minute < 10 ? 0 : ""}${minute}`;
  }
</script>

<script lang="ts">
  import Checkbox from "components/ui/checkbox.svelte";
  import RangeField from "components/ui/range-field.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import { formatDuration } from "formatting/date-time";

  export let data: SearchOptionsData;

  let sortBy = sortValues[0] as SortOption;

  $: data.sortBy = sortBy?.value ?? "price";

  function selectOperators(all: boolean): void {
    if (all) {
      data = { ...data, operators: operators.map((operator) => operator.id) };
    } else {
      data = { ...data, operators: [] };
    }
  }
</script>

<div class="search-options">
  <div class="sort">
    <h3 class="typography label-large">Sort by</h3>
    <SelectField options={sortValues} bind:value={sortBy} formatter={formatSortBy} />
  </div>

  <hr />

  <div class="stops">
    <h3 class="typography label-large">Stops</h3>

    <div class="options typography body-small">
      <label for="stop-direct">
        <Checkbox id="stop-direct" value="direct" bind:group={data.stops} /> Direct
      </label>
      <label for="non-stop">
        <Checkbox id="non-stop" value="non-stop" bind:group={data.stops} /> Non-stop
      </label>
      <label for="indirect">
        <Checkbox id="indirect" value="indirect" bind:group={data.stops} /> Indirect
      </label>
    </div>
  </div>

  <hr />

  <div class="departure-time">
    <h3 class="typography label-large">Departure time</h3>

    <div>
      <h4 class="typography label-medium bold">Departure</h4>
      <span class="typography body-small">
        {formatTime(data.departureSpan.start)} - {formatTime(data.departureSpan.end)}
      </span>
      <RangeField bind:value={data.departureSpan} min={0} max={1440} />
    </div>

    <div>
      <h4 class="typography label-medium bold">Arrival</h4>
      <span class="typography body-small">
        {formatTime(data.arrivalSpan.start)} - {formatTime(data.arrivalSpan.end)}
      </span>
      <RangeField bind:value={data.arrivalSpan} min={0} max={1440} />
    </div>
  </div>

  <hr />

  <div class="duration">
    <h3 class="typography label-large">Journey duration</h3>

    <span class="typography body-small">
      {formatDuration(123 * 60)} - {formatDuration(data.duration * 60)}
    </span>
    <RangeField bind:value={data.duration} min={123} max={492} />
  </div>

  <hr />

  <div class="operators">
    <h3 class="typography label-large">Railway operators</h3>

    <div class="actions">
      <button
        class="typography body-small bold"
        on:click={selectOperators.bind(selectOperators, true)}
      >
        Select all
      </button>
      <button
        class="typography body-small bold"
        on:click={selectOperators.bind(selectOperators, false)}
      >
        Clear all
      </button>
    </div>

    <ul class="typography body-small">
      {#each operators as operator}
        <li class="operator">
          <label for="operator-{operator.id}">
            <Checkbox id="operator-{operator.id}" value={operator.id} bind:group={data.operators} />
            {operator.name}
          </label>
        </li>
      {/each}
    </ul>
  </div>
</div>

<style>
  .search-options {
    display: flex;
    flex-flow: column;
    gap: 16px;
    padding: 16px 24px;
    overflow-y: auto;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  hr {
    margin: 0;
    border: 0;
    border-bottom: var(--color-common-line-medium) 1px solid;
  }

  h3 {
    margin-bottom: 16px;
  }

  .sort > :global(.select-field) {
    --height: 40px;
  }

  .operator > label {
    display: flex;
    gap: 8px;
    align-items: center;
    user-select: none;
  }

  .stops > .options {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .stops > .options > label {
    display: flex;
    gap: 8px;
    align-items: center;
    user-select: none;
  }

  .departure-time {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .departure-time > h3 {
    margin: 0;
  }

  .departure-time > div {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .duration {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .duration > h3 {
    margin-bottom: 8px;
  }

  .operators > .actions {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
  }

  .operators > .actions > button {
    padding: 0;
    color: var(--color-common-light-text-link);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .operators > ul {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }
</style>
