<script lang="ts" context="module">
  export const passengerPickerData = z
    .object({
      seniors65: z.number().min(0),
      seniors60: z.number().min(0),
      adults: z.number().min(0),
      youths15: z.number().min(0),
      youths12: z.number().min(0),
      children6: z.number().min(0),
      children4: z.number().min(0),
      children0: z.number().min(0),
    })
    .superRefine((arg, ctx) => {
      if (Object.values(arg).reduce((prev, curr) => prev + curr, 0) === 0) {
        ctx.addIssue({ message: "At least one passenger is mandatory", code: "custom" });
      }
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

  $: totalPassengerCount = Object.values(passengers).reduce((prev, curr) => prev + curr, 0);
  $: passengerInfo = `${totalPassengerCount} Passenger${totalPassengerCount === 1 ? "" : "s"}`;
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
      {passengerInfo}
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
        <PassengerCounter label="Senior (65+)" bind:amount={passengers.seniors65} />
        <PassengerCounter label="Senior (60-64)" bind:amount={passengers.seniors60} />
        <PassengerCounter label="Adult (26-59)" bind:amount={passengers.adults} />
        <PassengerCounter label="Youth (15-25)" bind:amount={passengers.youths15} />
        <PassengerCounter label="Youth (12-14)" bind:amount={passengers.youths12} />
        <PassengerCounter label="Child (6-11)" bind:amount={passengers.children6} />
        <PassengerCounter label="Child (4-5)" bind:amount={passengers.children4} />
        <PassengerCounter label="Child (0-3)" bind:amount={passengers.children0} />
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
    margin-top: 8px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
