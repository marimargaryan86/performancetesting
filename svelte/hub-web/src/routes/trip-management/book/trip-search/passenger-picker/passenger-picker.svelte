<script lang="ts" context="module">
  export const passengerPickerData = z.object({
    adults: z.number().min(1, "At least one adult is mandatory"),
    children: z.number().min(0),
    infants: z.number().min(0),
  });

  export type PassengerPickerData = z.infer<typeof passengerPickerData>;
</script>

<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import PassengerCounter from "./passenger-counter.svelte";
  import { scale } from "svelte/transition";
  import { z } from "zod";
  import { slideFade } from "transitions/slide-fade";

  export let passengers: PassengerPickerData;
  export let error: string | string[] | boolean = false;

  let expanded = false;

  $: passengerInfo = [
    passengers.adults
      ? `${passengers.adults} Adult${passengers.adults === 1 ? "" : "s"}`
      : undefined,
    passengers.children
      ? `${passengers.children} Child${passengers.children === 1 ? "" : "ren"}`
      : undefined,
    passengers.infants
      ? `${passengers.infants} Infant${passengers.infants === 1 ? "" : "s"}`
      : undefined,
  ]
    .filter((passenger): passenger is string => Boolean(passenger))
    .join(", ");
  $: totalPassengerCount = Object.values(passengers).reduce((prev, curr) => prev + curr, 0);
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
    <span class="typography title-small bold title-small bold">
      {#if totalPassengerCount > 0}
        {passengerInfo}
      {:else}
        Passengers
      {/if}
    </span>

    <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-main-primary-500)" />
  </button>

  {#if typeof displayError === "string"}
    <span class="error-message" transition:slideFade={{ duration: 300 }}>{displayError}</span>
  {/if}

  {#if expanded}
    <div class="dialogue" transition:scale={{ duration: 150, start: 0.8 }}>
      <div class="header typography title-medium bold title-medium bold">Passengers</div>

      <div class="counters">
        <PassengerCounter label="Adult" bind:amount={passengers.adults} />
        <PassengerCounter label="Children (2-11)" bind:amount={passengers.children} />
        <PassengerCounter label="Infants (under 2)" bind:amount={passengers.infants} />
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
    z-index: 100;
    width: 300px;
    margin-top: 4px;
    padding: 20px;
    color: var(--color-main-neutral-900);
    background: #ffffff;
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgb(17 24 39 / 0.05), 0 12px 16px rgb(17 24 39 / 0.1);
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
    display: block;
    margin-top: 8px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
