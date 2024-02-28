<script lang="ts">
  import { formatAmount } from "$lib/formatting/currency";
  import { getLocale, getTranslator } from "$lib/i18n";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { afterUpdate, createEventDispatcher, type ComponentEvents, onMount } from "svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import OfferOptions, { OPTION_EXPANSION_TIME_MS } from "./offer-options.svelte";
  import Itinerary from "./itinerary.svelte";

  const t = getTranslator();
  const locale = getLocale();
  const dispatch = createEventDispatcher<{
    mark: ComponentEvents<OfferOptions>["mark"]["detail"];
    select: ComponentEvents<OfferOptions>["select"]["detail"];
  }>();

  export let group: MobileSchemas.OfferGroup;
  export let selectedOption: MobileSchemas.OfferOption | undefined;
  export let finalSelection: boolean;

  let container: HTMLDivElement | undefined;

  $: defaultOption = group.options[0];
  $: groupSelected = group.optionIds.some((id) => id === selectedOption?.id);
  $: expanded = groupSelected;

  function mark(option: MobileSchemas.OfferOption): void {
    dispatch("mark", { option });
  }

  function select(event: ComponentEvents<OfferOptions>["select"]): void {
    dispatch("select", event.detail);

    if (!container) {
      return;
    }

    const target = document.querySelector(
      `.trip-summary.${finalSelection ? "inbound" : "outbound"}`,
    );

    if (!target) {
      return;
    }

    const targetBcr = target.getBoundingClientRect();
    const placeholderBcr = container.getBoundingClientRect();
    const placeholder = container.cloneNode(true) as HTMLDivElement;

    const transitionTimeMs = 800;
    placeholder.style.width = `${placeholderBcr.width}px`;
    placeholder.style.height = `${placeholderBcr.height}px`;
    placeholder.style.pointerEvents = "none";
    placeholder.style.userSelect = "none";
    placeholder.style.position = "absolute";
    placeholder.style.left = `${placeholderBcr.left}px`;
    placeholder.style.top = `${placeholderBcr.top}px`;
    placeholder.style.transition = `transform ${transitionTimeMs}ms ease, top ${transitionTimeMs}ms ease, left ${transitionTimeMs}ms ease, opacity ${transitionTimeMs}ms ease 200ms`;
    placeholder.style.transformOrigin = "top left";
    placeholder.style.opacity = "1";

    document.body.append(placeholder);
    setTimeout(() => {
      placeholder.style.opacity = "0.2";
      placeholder.style.left = `${targetBcr.left}px`;
      placeholder.style.top = `${targetBcr.top}px`;
      placeholder.style.transform = `scale(${targetBcr.width / placeholderBcr.width}, ${targetBcr.height / placeholderBcr.height})`;

      setTimeout(() => placeholder.remove(), transitionTimeMs);
    }, 10);
  }

  function scrollIntoView(): void {
    if (groupSelected) {
      container?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  afterUpdate(() => {
    setTimeout(scrollIntoView, OPTION_EXPANSION_TIME_MS);
  });

  onMount(() => {
    scrollIntoView();
  });
</script>

<div bind:this={container} class="offer-group" class:selected={groupSelected}>
  <Itinerary detailsList={group.detailsList} />

  {#if defaultOption}
    <div class="summary">
      <span class="price">
        <span typography="label-medium">{$t("sentences.startingAt")}</span>
        <strong typography="title-large" weight="bold">
          {formatAmount(defaultOption.price.total, $locale, { sign: true })}
        </strong>
      </span>

      {#if !expanded}
        <button
          transition:slideFade={{ duration: OPTION_EXPANSION_TIME_MS }}
          variant="outline"
          size="x-small"
          on:click={mark.bind(mark, defaultOption)}
        >
          {$t("actions.select")}
        </button>
      {/if}
    </div>
  {/if}

  {#if defaultOption && expanded}
    <OfferOptions
      {group}
      {defaultOption}
      {groupSelected}
      {selectedOption}
      {finalSelection}
      on:select={select}
      on:mark
    />
  {/if}
</div>

<style>
  .offer-group {
    display: grid;
    grid-template-columns: 1fr max-content;
    gap: 32px 16px;
    padding: 16px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  .offer-group.selected {
    border-color: var(--color-main-primary-700);
    box-shadow: 0 0 0 1px var(--color-main-primary-700) inset;
  }

  .summary {
    display: flex;
    flex-flow: column;
    gap: 16px;
    align-items: flex-end;
    justify-content: space-between;
  }

  .price {
    display: flex;
    gap: 4px;
    align-items: center;
  }
</style>
