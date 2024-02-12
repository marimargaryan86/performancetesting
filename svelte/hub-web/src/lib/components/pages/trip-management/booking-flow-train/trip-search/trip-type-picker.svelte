<script lang="ts">
  import { scale } from "svelte/transition";
  import { createSelect, melt } from "@melt-ui/svelte";
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import Icon from "$lib/components/icons/icon.svelte";
  import { getTranslator } from "$lib/i18n";
  import { TRIP_TYPES, type TripType } from "$lib/models/trip-offer-search";

  export let value: TripType = "one-way";

  const t = getTranslator();

  const {
    elements: { trigger, menu, option, label: meltLabel },
    states: { selected, open },
    helpers: { isHighlighted, isSelected },
  } = createSelect<TripType>({
    forceVisible: true,
    positioning: {
      placement: "bottom-start",
      fitViewport: true,
    },
    defaultSelected: {
      value,
      label: $t(`tripTypes.${value}`),
    },
    highlightOnHover: true,
  });

  $: value = $selected?.value ?? "one-way";
  $: updateInternalValue(value);

  function updateInternalValue(nextValue: TripType): void {
    $selected = { label: $t(`tripTypes.${nextValue}`), value: nextValue };
  }
</script>

<button use:melt={$trigger} type="button">
  <span class="label" typography="title-small" weight="bold" use:melt={$meltLabel}>
    {#if value === "one-way"}
      <span>{"->"}</span>
    {:else}
      <Icon variant="swap-directions" color="var(--color-main-primary-500)" size="16px" />
    {/if}

    <span>{$t(`tripTypes.${value}`)}</span>

    <ChevronIcon direction={$open ? "up" : "down"} color="var(--color-main-primary-500)" />
  </span>

  {#if $open}
    <ul class="options" use:melt={$menu} transition:scale={{ duration: 150, start: 0.8 }}>
      {#each [...TRIP_TYPES] as item}
        <li
          typography="body-medium"
          class="option"
          use:melt={$option({ value: item, label: $t(`tripTypes.${item}`) })}
          class:highlighted={$isHighlighted(item)}
        >
          {#if $isSelected(item)}
            <Icon variant="checked" size="16px" color="var(--color-main-primary-500)" />
          {:else}
            <span />
          {/if}
          {$t(`tripTypes.${item}`)}
        </li>
      {/each}
    </ul>
  {/if}
</button>

<style>
  button {
    display: flex;
    gap: 8px;
    align-items: center;
    height: var(--x-height);
    color: var(--color-main-primary-500);
    background-color: transparent;
    border: 0;
    cursor: pointer;
    user-select: none;
  }

  .label {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .options {
    padding: 8px 0;
    color: var(--color-main-neutral-900);
    background: var(--color-common-background-light-main);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
    box-shadow:
      0 4px 6px rgb(17 24 39 / 0.05),
      0 12px 16px rgb(17 24 39 / 0.1);
    transform-origin: top left;
  }

  .option {
    display: grid;
    grid-template-columns: 16px 1fr;
    gap: 8px;
    align-items: center;
    padding: 8px 24px 8px 8px;
    cursor: pointer;
    user-select: none;
  }

  .option.highlighted {
    background-color: var(--color-common-background-light-green);
  }
</style>
