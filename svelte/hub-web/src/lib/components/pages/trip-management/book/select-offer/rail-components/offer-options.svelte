<script lang="ts" context="module">
  export const OPTION_EXPANSION_TIME_MS = 500;
</script>

<script lang="ts">
  import Icon from "$lib/components/icons/icon.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { formatAmount } from "$lib/formatting/currency";
  import { getLocale, getTranslator } from "$lib/i18n";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { createEventDispatcher } from "svelte";
  import { writable, type Writable } from "svelte/store";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

  const t = getTranslator();
  const locale = getLocale();
  const dispatch = createEventDispatcher<{
    select: { option: MobileSchemas.OfferOption; pending: Writable<boolean> };
    mark: { option: MobileSchemas.OfferOption };
  }>();

  export let group: MobileSchemas.OfferGroup;
  export let defaultOption: MobileSchemas.OfferOption;
  export let selectedOptionId: string | undefined;
  export let groupSelected: boolean;
  export let finalSelection: boolean;

  const pending = writable(false);

  function select(): void {
    const nextOption = group.options.find((option) => option.id === selectedOptionId);

    dispatch("select", { option: nextOption ?? defaultOption, pending });
  }

  function mark(option: MobileSchemas.OfferOption): void {
    dispatch("mark", { option });
  }
</script>

<div class="offer-options" transition:slideFade={{ duration: OPTION_EXPANSION_TIME_MS }}>
  <ul class="options">
    {#each group.options as option}
      {@const selected = option.id === selectedOptionId}

      <li class="option" class:selected>
        <span typography="body-large" weight="bold">{option.brandName}</span>

        <strong typography="body-medium" weight="bold">
          {formatAmount(option.price.total, $locale, { sign: true })}
        </strong>

        <button
          variant={selected ? "primary" : "outline"}
          size="x-small"
          on:click={mark.bind(mark, option)}
        >
          {#if selected}
            <Icon variant="checked" size="16px" />
            {$t("words.selected")}
          {:else}
            {$t("actions.select")}
          {/if}
        </button>
      </li>
    {/each}
  </ul>

  <button variant="primary" size="medium" disabled={!groupSelected} on:click={select}>
    {#if finalSelection}
      {$t("actions.bookNow")}

      {#if $pending}
        <LoadingIcon />
      {/if}
    {:else}
      {$t("actions.confirmSelection")}
    {/if}
  </button>
</div>

<style>
  .offer-options {
    display: flex;
    flex-flow: column;
    grid-column: 1 / -1;
    gap: 8px;
    width: 100%;
    overflow: hidden;
  }

  .options {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    scrollbar-width: thin;
  }

  .option {
    display: flex;
    flex-flow: column;
    flex-shrink: 0;
    gap: 8px;
    width: 180px;
    padding: 16px;
    background-color: var(--color-main-primary-50);
    border: transparent 2px solid;
    border-radius: 8px;
  }

  .option.selected {
    border-color: var(--color-main-primary-500);
  }

  .option > span {
    flex-grow: 1;
    color: var(--color-main-primary-700);
    line-height: 1.2;
  }

  .option > strong {
    padding: 8px 0 0;
    text-align: right;
    border-top: var(--color-common-dark-medium) 1px solid;
  }
</style>
