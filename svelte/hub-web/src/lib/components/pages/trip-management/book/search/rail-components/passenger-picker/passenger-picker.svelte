<script lang="ts">
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import { clickOutside } from "$lib/directives/click-outside";
  import PassengerCounter from "./passenger-counter.svelte";
  import { scale } from "svelte/transition";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { getTranslator } from "$lib/i18n";
  import { getPassengerFullLabel, type PassengerPickerData } from "$lib/models/passenger";

  export let passengers: PassengerPickerData;
  export let error: string | string[] | boolean = false;

  const t = getTranslator();
  const passengerKeys = Object.keys(passengers) as unknown as (keyof PassengerPickerData)[];

  let expanded = false;

  $: totalCount = Object.values(passengers).reduce((prev, curr) => prev + curr, 0);
  $: displayError = error instanceof Array ? error.join(", ") : error;
  $: passengers, (error = false);

  function open(): void {
    expanded = true;
  }

  function close(): void {
    expanded = false;
  }

  function toggle(): void {
    if (expanded) {
      close();
    } else {
      open();
    }
  }
</script>

<div class="passenger-picker" use:clickOutside={close}>
  <button on:click={toggle} type="button">
    <span typography="title-small" weight="bold">
      {totalCount}
      {$t("words.passenger", { count: totalCount })}
    </span>

    <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-main-primary-500)" />
  </button>

  {#if typeof displayError === "string"}
    <span class="error-message" transition:slideFade={{ duration: 300 }}>{displayError}</span>
  {/if}

  {#if expanded}
    <div class="dialogue" transition:scale={{ duration: 150, start: 0.8 }}>
      <div class="header" typography="title-medium" weight="bold">
        {$t("words.passenger_other")}
      </div>

      <div class="counters">
        {#each passengerKeys as key}
          <PassengerCounter
            label={getPassengerFullLabel(key, $t)}
            bind:count={passengers[key]}
            {totalCount}
          />
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .passenger-picker {
    --x-height: 22px;

    position: relative;
    display: inline-block;
  }

  button {
    display: flex;
    gap: 8px;
    align-items: center;
    height: var(--x-height);
    color: var(--color-main-primary-500);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .dialogue {
    position: absolute;
    top: var(--x-height);
    left: 0;
    z-index: var(--z-index-ui-dialog);
    width: 300px;
    margin-top: 4px;
    padding: 20px;
    color: var(--color-main-neutral-900);
    background: #ffffff;
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
    box-shadow:
      0 4px 6px rgb(17 24 39 / 0.05),
      0 12px 16px rgb(17 24 39 / 0.1);
    transform-origin: top left;
  }

  .header {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    white-space: nowrap;
  }

  .counters {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .error-message {
    margin-top: 8px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
