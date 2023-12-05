<script lang="ts" context="module">
  export const MAX_TOTAL_COUNT = 9;
  export const PASSENGER_DEFINITIONS: Record<
    keyof PassengerPickerData,
    { label: { singular: string; plural: string }; span: { from: number; to?: number } }
  > = {
    seniors65: { label: { singular: "Senior", plural: "Seniors" }, span: { from: 65 } },
    seniors60: { label: { singular: "Senior", plural: "Seniors" }, span: { from: 60, to: 64 } },
    adults: { label: { singular: "Adult", plural: "Adults" }, span: { from: 26, to: 59 } },
    youths15: { label: { singular: "Youth", plural: "Youths" }, span: { from: 15, to: 25 } },
    youths12: { label: { singular: "Youth", plural: "Youths" }, span: { from: 12, to: 14 } },
    children6: { label: { singular: "Child", plural: "Children" }, span: { from: 6, to: 11 } },
    children4: { label: { singular: "Child", plural: "Children" }, span: { from: 4, to: 5 } },
    children0: { label: { singular: "Child", plural: "Children" }, span: { from: 0, to: 3 } },
  };

  export function getPassengerFullLabel(
    def: (typeof PASSENGER_DEFINITIONS)[keyof PassengerPickerData],
    which: "singular" | "plural" = "singular",
  ): string {
    return `${def.label[which]} (${def.span.from}${
      def.span.to === undefined ? "+" : `-${def.span.to}`
    })`;
  }

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

  export function getPassengersPresentation(passengers: PassengerPickerData): string {
    return Object.entries(PASSENGER_DEFINITIONS)
      .map(([key, val]) => {
        const type = key as keyof PassengerPickerData;

        if (!passengers[type]) {
          return undefined;
        }

        return `${passengers[type]} ${getPassengerFullLabel(
          val,
          passengers[type] === 1 ? "singular" : "plural",
        )}`;
      })
      .filter(ensureDefined)
      .join(", ");
  }
</script>

<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import PassengerCounter from "./passenger-counter.svelte";
  import { scale } from "svelte/transition";
  import { z } from "zod";
  import { slideFade } from "transitions/slide-fade";
  import { ensureDefined } from "utils/array";

  export let passengers: PassengerPickerData;
  export let error: string | string[] | boolean = false;

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
    <span class="typography title-small bold title-small bold">
      {`${totalCount} Passenger${totalCount === 1 ? "" : "s"}`}
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
        {#each passengerKeys as key}
          <PassengerCounter
            label={getPassengerFullLabel(PASSENGER_DEFINITIONS[key])}
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
    z-index: 100;
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
