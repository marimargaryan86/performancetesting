<script lang="ts" context="module">
  const sortOptions = [
    "lowest-price",
    "fastest",
    "earliest-departure",
    "latest-departure",
    "earliest-arrival",
    "latest-arrival",
  ] as const;
  export type SortOption = (typeof sortOptions)[number];

  type StopValue = "direct";
  type TimeSpan = { start: number; end: number };

  export type SearchOptionsData = {
    sortBy: SortOption;
    stops: StopValue[];
    departureSpanM: TimeSpan;
    arrivalSpanM: TimeSpan;
    durationM: number;
    vendors: string[];
  };

  export type SearchOptionsSettings = {
    durationSpanM: { start: number; end: number };
    vendors: string[];
  };

  function formatTime(minutes: number): string {
    const hours = Math.floor(minutes / 60);
    const minute = minutes % 60;

    return `${hours < 10 ? 0 : ""}${hours}:${minute < 10 ? 0 : ""}${minute}`;
  }

  function getFormatSortOptionFunc(locale: LocaleData): (value?: SortOption) => string {
    return (value) => (value ? locale.sortOptions[value] : locale.sortOptions["lowest-price"]);
  }
</script>

<script lang="ts">
  import Checkbox from "components/ui/checkbox.svelte";
  import RangeField from "components/ui/range-field.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import { formatDuration } from "formatting/date-time";
  import { getLocaleData, type LocaleData } from "i18n";

  export let data: SearchOptionsData;
  export let settings: SearchOptionsSettings;

  const i18n = getLocaleData();

  $: formatSortOption = getFormatSortOptionFunc($i18n);

  function selectOperators(all: boolean): void {
    if (all) {
      data = { ...data, vendors: [...settings.vendors] };
    } else {
      data = { ...data, vendors: [] };
    }
  }
</script>

<div class="search-options">
  <div class="sort">
    <h3 typography="label-large">{$i18n.actions.sortBy}</h3>
    <SelectField options={sortOptions} bind:value={data.sortBy} formatter={formatSortOption} />
  </div>

  <hr />

  <div class="stops">
    <h3 typography="label-large">{$i18n.words.stop.plural}</h3>
    <div class="options" typography="body-small">
      <label for="stop-direct">
        <Checkbox id="stop-direct" value="direct" bind:group={data.stops} />
        {$i18n.words.direct}
      </label>
    </div>
  </div>

  <hr />

  <div class="departure-time">
    <h3 typography="label-large">{$i18n.words.departureTime}</h3>
    <div>
      <h4 typography="label-medium" weight="bold">{$i18n.words.departure}</h4>
      <span typography="body-small">
        {formatTime(data.departureSpanM.start)} - {formatTime(data.departureSpanM.end)}
      </span>
      <RangeField bind:value={data.departureSpanM} min={0} max={1440} />
    </div>

    <div>
      <h4 typography="label-medium" weight="bold">{$i18n.words.arrival}</h4>
      <span typography="body-small">
        {formatTime(data.arrivalSpanM.start)} - {formatTime(data.arrivalSpanM.end)}
      </span>
      <RangeField bind:value={data.arrivalSpanM} min={0} max={1440} />
    </div>
  </div>

  <hr />

  <div class="duration">
    <h3 typography="label-large">{$i18n.words.journeyDuration}</h3>
    <span typography="body-small">
      {formatDuration(data.durationM * 60)} - {formatDuration(settings.durationSpanM.end * 60)}
    </span>
    <RangeField
      bind:value={data.durationM}
      min={settings.durationSpanM.start}
      max={settings.durationSpanM.end}
    />
  </div>

  <hr />

  {#if settings.vendors.length}
    <div class="operators">
      <h3 typography="label-large">{$i18n.words.railwayOperators}</h3>

      <div class="actions">
        <button
          typography="body-small"
          weight="bold"
          on:click={selectOperators.bind(selectOperators, true)}
        >
          {$i18n.actions.selectAll}
        </button>
        <button
          typography="body-small"
          weight="bold"
          on:click={selectOperators.bind(selectOperators, false)}
        >
          {$i18n.actions.clearAll}
        </button>
      </div>

      <ul typography="body-small">
        {#each settings.vendors as vendor, idx}
          <li class="vendor">
            <label for="vendor-{idx}">
              <Checkbox id="vendor-{idx}" value={vendor} bind:group={data.vendors} />
              {vendor}
            </label>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
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

  .vendor > label {
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
