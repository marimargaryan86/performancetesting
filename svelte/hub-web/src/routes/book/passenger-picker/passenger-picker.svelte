<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import Dialogue from "./dialogue.svelte";

  export let adults = 0;
  export let children = 0;
  export let infants = 0;

  let expanded = false;
  let passengerInfo = "";

  $: passengerInfo = `${adults} Adult${adults > 1 ? "s" : ""}${children > 0 ? "," : ""}
    ${children > 0 ? `${children} Child${children > 1 ? "ren" : ""}` : ""}${infants > 0 ? "," : ""}
    ${infants > 0 ? `${infants} Infant${infants > 1 ? "s" : ""}` : ""}`;

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
  <div on:click={toggle} class="passenger-select">
    {#if adults + children + infants > 0}
      <span class="typography body-medium-weight-600">{passengerInfo}</span>
    {:else}
      <span class="typography body-medium-weight-600">Passengers</span>
    {/if}
    <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-main-primary-500)" />
  </div>

  {#if expanded}
    <Dialogue bind:adults bind:children bind:infants />
  {/if}
</div>

<style>
  .passenger-picker {
    --x-height: var(--height, 52px);
    --x-font-size: var(--font-size, 14px);
    --x-icon-padding: var(--icon-padding, 16px);

    position: relative;
    display: inline-block;
  }

  .passenger-select {
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--color-main-primary-500);
    cursor: pointer;
  }
</style>
