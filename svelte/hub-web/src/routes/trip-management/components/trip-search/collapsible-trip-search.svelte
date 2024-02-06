<script lang="ts">
  import Collapsible from "components/ui/collapsible.svelte";
  import { getPassengersPresentation } from "./passenger-picker/passenger-picker.svelte";
  import { getLocale, getLocaleData } from "i18n";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import type { SearchData } from "./trip-search.svelte";

  export let searchData: SearchData;

  const locale = getLocale();
  const i18n = getLocaleData();
</script>

<Collapsible>
  <div class="header" slot="always-visible" let:toggle let:expanded>
    <div class="overview">
      <div typography="body-large" class="orig-dest" weight="bold">
        {searchData.origin.name}
        <span typography="label-medium" weight="bold">{"->"}</span>
        {searchData.destination.name}
      </div>

      <div typography="label-large">
        {searchData.outbound.toLocaleDateString($locale, {
          weekday: "short",
          day: "numeric",
          month: "short",
        })}

        {#if searchData.tripType === "round-trip"}
          - {searchData.inbound.toLocaleDateString($locale, {
            weekday: "short",
            day: "numeric",
            month: "short",
          })}
        {/if}
        ·
        {$i18n.tripTypes[searchData.tripType]}
        ·
        {getPassengersPresentation(searchData.passengers, $i18n)}
      </div>
    </div>

    <button typography="body-medium" weight="bold" on:click={toggle}>
      {$i18n.actions.modifySearch}

      <ChevronIcon
        size="16px"
        color="var(--color-main-primary-500)"
        direction={expanded ? "up" : "down"}
      />
    </button>
  </div>

  <slot slot="default" />
</Collapsible>

<style>
  .header > button {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    margin: 0;
    padding: 0;
    color: var(--color-common-light-medium);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .header {
    display: flex;
    gap: 8px;
    max-width: 1152px;
    padding: 16px 24px;
  }

  .header > .overview {
    flex-grow: 1;
  }

  .orig-dest {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .orig-dest > span {
    color: var(--color-main-primary-500);
  }
</style>
