<script lang="ts">
  import { hourFormat } from "utils/date-time";
  import { afterUpdate, onMount } from "svelte";
  import { getTimeFormat } from "i18n";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import type { CalendarDateTime, DateValue } from "@internationalized/date";

  export let min: CalendarDateTime | undefined = undefined;
  export let value: CalendarDateTime | undefined = undefined;
  export let isDateDisabled: (date: DateValue) => boolean;

  const timeFormat = getTimeFormat();

  let timePickerFade = { left: 1, right: 0 };
  let timePickerInner: HTMLDivElement | undefined;
  let scrollToBhavior: ScrollBehavior | undefined;

  $: if (value) {
    ensureInRange(value);
  }

  export function scrollToSelected(behavior: ScrollBehavior): void {
    scrollToBhavior = behavior;
  }

  function ensureInRange(nextValue: DateValue): void {
    if (isDateDisabled(nextValue) && min) {
      setHour(min.hour);
    }
  }

  function setHour(hour: number): void {
    value = value?.set({ hour, minute: 0, second: 0 });
    scrollToSelected("smooth");
  }

  function scrollOptions(direction: "left" | "right"): void {
    if (!timePickerInner) {
      return;
    }

    const parentBcr = timePickerInner.getBoundingClientRect();
    const children = Array.from(timePickerInner.children as unknown as HTMLButtonElement[]);
    const nextChild = children.find((child) => {
      const childBcr = child.getBoundingClientRect();

      return (
        childBcr[direction] + (direction === "left" ? childBcr.width : 0) > parentBcr[direction]
      );
    });

    nextChild?.scrollIntoView({ behavior: "smooth", inline: "center" });
  }

  function adjustFade(event: UIEvent & { currentTarget: EventTarget & HTMLDivElement }): void {
    const { scrollLeft, scrollWidth, clientWidth } = event.currentTarget;
    timePickerFade.left = 1 - scrollLeft / 16;
    timePickerFade.right = 1 - (scrollWidth - scrollLeft - clientWidth) / 16;
  }

  afterUpdate(() => {
    if (scrollToBhavior) {
      timePickerInner
        ?.querySelector(".selected")
        ?.scrollIntoView({ behavior: scrollToBhavior, inline: "center" });

      scrollToBhavior = undefined;
    }
  });

  onMount(() => scrollToSelected("instant"));
</script>

<div
  class="time-picker"
  style:--left-fade={timePickerFade.left}
  style:--right-fade={timePickerFade.right}
>
  <button on:click={scrollOptions.bind(scrollOptions, "left")} type="button">
    <ChevronIcon size="24px" direction="left" />
  </button>

  <div class="options" typography="body-medium" bind:this={timePickerInner} on:scroll={adjustFade}>
    {#each hourFormat[$timeFormat] as item}
      <button
        class="option"
        type="button"
        on:click={setHour.bind(setHour, item.value)}
        class:selected={value?.hour === item.value}
        disabled={value && isDateDisabled(value.set({ hour: item.value, minute: 0, second: 0 }))}
      >
        {item.label}
      </button>
    {/each}

    <span class="fade left" />
    <span class="fade right" />
  </div>

  <button on:click={scrollOptions.bind(scrollOptions, "right")} type="button">
    <ChevronIcon size="24px" direction="right" />
  </button>
</div>

<style>
  .time-picker {
    display: grid;
    grid-template-columns: max-content 1fr max-content;
    align-items: center;
    margin-top: 16px;
    padding-top: 16px;
    border-top: var(--color-common-line-soft) 1px solid;
  }

  .time-picker > button {
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .time-picker > button > :global(svg) {
    vertical-align: top;
  }

  .options {
    position: relative;
    display: flex;
    gap: 8px;
    overflow-y: scroll;
    white-space: nowrap;
    scrollbar-width: none;

    /* stylelint-disable-next-line property-no-vendor-prefix */
    -webkit-mask-image: linear-gradient(
      90deg,
      rgb(0 0 0 / var(--left-fade)) 0,
      rgb(0 0 0 / 1) 40px,
      rgb(0 0 0 / 1) calc(100% - 40px),
      rgb(0 0 0 / var(--right-fade)) 100%
    );
    mask-image: linear-gradient(
      90deg,
      rgb(0 0 0 / var(--left-fade)) 0,
      rgb(0 0 0 / 1) 40px,
      rgb(0 0 0 / 1) calc(100% - 40px),
      rgb(0 0 0 / var(--right-fade)) 100%
    );
  }

  .option {
    padding: 8px 12px;
    color: var(--color-main-neutral-800);
    font-size: inherit;
    font-family: inherit;
    background-color: transparent;
    border: 0;
    border-radius: 8px;
    cursor: pointer;
    transition:
      color 150ms ease,
      background-color 150ms ease;
  }

  .option.selected {
    color: var(--color-common-light-text-link);
    background-color: var(--color-main-primary-50);
  }

  .option:disabled {
    color: var(--color-main-neutral-400);
  }

  .options::-webkit-scrollbar {
    display: none;
  }
</style>
