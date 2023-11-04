<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import Button from "components/ui/button.svelte";
  import { formatAmount } from "formatting/currency";
  import type { OfferOption } from "integration/junction-mobile-api/schemas/offer";
  import { createEventDispatcher } from "svelte";
  import { slide } from "svelte/transition";

  export let options: OfferOption[];
  export let selectedOptions: OfferOption[];

  let expanded = false;

  const dispatch = createEventDispatcher<{
    select: OfferOption;
  }>();

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

  function select(option: OfferOption): void {
    dispatch("select", option);
  }
</script>

<div class="alternative-fares">
  <button class="toggle typography body-medium bold" on:click={toggle}>
    Alternative fares
    <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-main-primary-500)" />
  </button>

  {#if expanded}
    <ul transition:slide={{ duration: 200 }} class="options">
      {#each options as option}
        {@const selected = Boolean(selectedOptions.find((item) => item.id === option.id))}

        <li class="option">
          <strong class="typography body-xlarge bold">{option.brandName}</strong>

          <hr />

          <span class="typography body-medium bold">
            {formatAmount(option.price.total, undefined, true)}
          </span>

          <Button
            size="x-small"
            variant={selected ? "primary" : "outline"}
            on:click={select.bind(select, option)}
          >
            {#if selected}
              <span class="selected" />
              Selected
            {:else}
              Select
            {/if}
          </Button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .alternative-fares {
    display: flex;
    flex-flow: column;
  }

  .toggle {
    display: inline-flex;
    gap: 8px;
    align-self: flex-end;
    padding: 0;
    color: var(--color-main-primary-500);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .options {
    display: flex;
    gap: 16px;
    margin-top: 8px;
    overflow-y: auto;
  }

  .option {
    display: flex;
    flex-flow: column;
    flex-shrink: 0;
    gap: 16px;
    width: 160px;
    padding: 16px;
    background-color: var(--color-main-primary-50);
    border-radius: 16px;
  }

  .option > strong {
    color: var(--color-main-primary-700);
  }

  .option > hr {
    margin: 0;
    border: 0;
    border-top: var(--color-common-dark-medium) 1px solid;
  }

  .option > span {
    align-self: flex-end;
  }

  .option > :global(button) {
    display: inline-flex;
    gap: 8px;
    align-items: center;
  }

  .selected {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    background-color: var(--color-common-dark-strong);
    border-radius: 50%;
  }

  .selected::after {
    display: block;
    width: 5px;
    height: 8px;
    border: var(--color-main-primary-500) 0 solid;
    border-right-width: 2px;
    border-bottom-width: 2px;
    transform: translateY(-0.5px) rotateZ(45deg);
    content: "";
  }
</style>
