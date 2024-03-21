<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import { TRIP_TYPES, type TripType } from "../trip-search-data";

  export let value: TripType = "one-way";

  const t = getTranslator();
</script>

<div class="trip-type-picker" typography="label-large">
  {#each TRIP_TYPES as tripType}
    <!-- TODO(2024-03-20/alvin.s): In E2E, use the `testid` only when other selector strats fail.-->
    <label data-testid={tripType}>
      <input type="radio" bind:group={value} value={tripType} />
      <span>{$t(`tripTypes.${tripType}`)}</span>
    </label>
  {/each}
</div>

<style>
  .trip-type-picker {
    display: inline-flex;
    gap: 8px;
  }

  label {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  input {
    margin: 0;
  }
</style>
