<script lang="ts">
  import Checkbox from "$lib/components/ui/checkbox.svelte";
  import RangeField from "$lib/components/ui/range-field.svelte";
  import SelectField from "$lib/components/ui/select-field.svelte";
  import { formatDuration } from "$lib/formatting/date-time";
  import { getTranslator } from "$lib/i18n";
  import {
    getFormatSortOptionFunc,
    OFFER_SORT_OPTIONS,
    type SearchOptionsData,
    type SearchOptionsSettings,
    formatTime,
  } from "$lib/utils/offer";

  export let data: SearchOptionsData;
  export let settings: SearchOptionsSettings;

  const t = getTranslator();

  $: formatSortOption = getFormatSortOptionFunc($t);

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
    <h3 typography="label-large">{$t("actions.sortBy")}</h3>
    <SelectField
      options={OFFER_SORT_OPTIONS}
      bind:value={data.sortBy}
      formatter={formatSortOption}
    />
  </div>

  <hr />

  <div class="stops">
    <h3 typography="label-large">{$t("words.stop_other")}</h3>
    <div class="options" typography="body-small">
      <label for="stop-direct">
        <Checkbox id="stop-direct" value="direct" bind:group={data.stops} />
        {$t("words.stop_zero")}
      </label>
    </div>
  </div>

  <hr />

  <div class="departure-time">
    <h3 typography="label-large">{$t("words.departureTime")}</h3>
    <div>
      <h4 typography="label-medium" weight="bold">{$t("words.departure")}</h4>
      <span typography="body-small">
        {formatTime(data.departureSpanM.start)} - {formatTime(data.departureSpanM.end)}
      </span>
      <RangeField bind:value={data.departureSpanM} min={0} max={1440} />
    </div>

    <div>
      <h4 typography="label-medium" weight="bold">{$t("words.arrival")}</h4>
      <span typography="body-small">
        {formatTime(data.arrivalSpanM.start)} - {formatTime(data.arrivalSpanM.end)}
      </span>
      <RangeField bind:value={data.arrivalSpanM} min={0} max={1440} />
    </div>
  </div>

  <hr />

  <div class="duration">
    <h3 typography="label-large">{$t("words.journeyDuration")}</h3>
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
      <h3 typography="label-large">{$t("words.railwayOperators")}</h3>

      <div class="actions">
        <button
          typography="body-small"
          weight="bold"
          on:click={selectOperators.bind(selectOperators, true)}
        >
          {$t("actions.selectAll")}
        </button>
        <button
          typography="body-small"
          weight="bold"
          on:click={selectOperators.bind(selectOperators, false)}
        >
          {$t("actions.clearAll")}
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
