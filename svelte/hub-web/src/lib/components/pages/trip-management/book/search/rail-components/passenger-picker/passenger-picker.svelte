<script lang="ts" context="module">
  type PartialPassengerEntry = Partial<PassengerEntry>;
  type PartialPassengerPickerData = PartialPassengerEntry[];
</script>

<script lang="ts">
  import type { z } from "zod";
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import { clickOutside } from "$lib/directives/click-outside";
  import { scale } from "svelte/transition";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { getTranslator } from "$lib/i18n";
  import {
    MAX_TOTAL_COUNT,
    PASSENGER_DEFINITIONS,
    PASSENGER_TYPES,
    getPassengerAgeSpan,
    passengerPickerData,
    type PassengerEntry,
    type PassengerPickerData,
    type PassengerType,
  } from "$lib/models/passenger";
  import TextField from "$lib/components/ui/text-field.svelte";

  export let passengers: PartialPassengerPickerData;
  export let error: string | string[] | boolean = false;

  const t = getTranslator();

  let expanded = false;
  let ageErrors: z.ZodFormattedError<PassengerPickerData> | undefined = undefined;

  $: totalCount = passengers.length;
  $: displayError = error instanceof Array ? error.join(", ") : error;
  $: passengers, (error = false);

  function open(): void {
    expanded = true;
  }

  function close(): void {
    clearAgeErrors();

    const validation = passengerPickerData.safeParse(passengers);

    if (!validation.success) {
      ageErrors = validation.error.format();
      return;
    }

    expanded = false;
  }

  function toggle(): void {
    if (expanded) {
      close();
    } else {
      open();
    }
  }

  function clearAgeErrors(): void {
    ageErrors = undefined;
  }

  function addPassenger(type: PassengerType): void {
    clearAgeErrors();

    if (passengers.length === MAX_TOTAL_COUNT) {
      return;
    }

    passengers = [...passengers, { type }];
  }

  function removePassenger(type: PassengerType): void {
    clearAgeErrors();

    passengers = [
      ...passengers.filter((passenger) => passenger.type !== type),
      ...passengers.filter((passenger) => passenger.type === type).slice(0, -1),
    ];
  }

  function removePassengerItem(passenger: PartialPassengerEntry): void {
    clearAgeErrors();

    passengers = passengers.filter((item) => item !== passenger);
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
    <div class="dialog" transition:scale={{ duration: 150, start: 0.8 }}>
      <div class="header" typography="title-medium" weight="bold">
        {$t("words.passenger_other")}
      </div>

      <div class="passengers">
        {#each PASSENGER_TYPES as passengerType}
          {@const items = passengers.filter((passenger) => passenger.type === passengerType)}

          <div typography="body-medium" class="passenger-type">
            <div class="passenger-label">
              <span weight="bold">{$t(`passengerTypes.${passengerType}`, { count: 2 })}</span>
              <em typography="body-small">{getPassengerAgeSpan(passengerType)}</em>
            </div>

            <div class="counter">
              <button
                variant="primary"
                size="xx-small"
                type="button"
                on:click|stopPropagation={removePassenger.bind(removePassenger, passengerType)}
              >
                -
              </button>

              <span class="passenger-count">{items.length}</span>

              <button
                variant="primary"
                size="xx-small"
                type="button"
                on:click|stopPropagation={addPassenger.bind(addPassenger, passengerType)}
              >
                +
              </button>
            </div>

            {#if passengerType !== "adult" && items.length}
              <ul class="ages">
                {#each items as item}
                  {@const idx = passengers.indexOf(item)}
                  <li class="age">
                    <TextField
                      type="number"
                      bind:value={item.age}
                      placeholder={$t("actions.enterAge")}
                      min={PASSENGER_DEFINITIONS[passengerType].from}
                      max={PASSENGER_DEFINITIONS[passengerType].to}
                    />

                    <button
                      variant="outline"
                      size="xx-small"
                      type="button"
                      on:click|stopPropagation={removePassengerItem.bind(removePassengerItem, item)}
                    >
                      -
                    </button>

                    {#if ageErrors?.[idx]?.age?._errors}
                      <span class="error-message" transition:slideFade={{ duration: 300 }}>
                        {ageErrors[idx]?.age?._errors.join(", ")}
                      </span>
                    {/if}
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
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

  button:not([variant]) {
    display: flex;
    gap: 8px;
    align-items: center;
    height: var(--x-height);
    color: var(--color-main-primary-500);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .dialog {
    position: absolute;
    top: var(--x-height);
    left: 0;
    z-index: var(--z-index-ui-dialog);
    width: 340px;
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

  .passengers {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .passenger-type {
    display: grid;
    grid-template-columns: 1fr max-content;
    gap: 8px;
    align-items: center;
  }

  .passenger-label {
    display: flex;
    flex-flow: column;
    gap: 2px;
  }

  .passenger-label > em {
    color: var(--color-common-light-medium);
  }

  .counter {
    display: grid;
    grid-template-columns: 32px 32px 32px;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .ages {
    display: flex;
    flex-flow: column;
    grid-column: 1 / -1;
    gap: 4px;
  }

  .age {
    display: grid;
    grid-template-columns: 1fr 32px;
    gap: 4px;
  }

  .age > :global(.text-field) {
    --x-height: 32px;
    --x-icon-padding: 12px;

    width: 100%;
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

  .age > .error-message {
    grid-column: 1 / -1;
    margin-top: 0;
  }
</style>
