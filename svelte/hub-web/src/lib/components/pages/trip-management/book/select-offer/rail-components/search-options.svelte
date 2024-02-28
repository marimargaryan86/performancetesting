<script lang="ts">
  import SelectField from "$lib/components/ui/select-field.svelte";
  import { formatOfferSortOption } from "$lib/formatting/offer";
  import { getTranslator } from "$lib/i18n";
  import { offerSortOptions, type OfferSortOption } from "$lib/sorting/offer";

  const t = getTranslator();

  export let sortBy: OfferSortOption;
  export let directOnly: boolean;
</script>

<div class="search-options">
  <label for="sort-by" typography="label-large" class="vertical">
    {$t("actions.sortBy")}

    <SelectField
      id="sort-by"
      bind:value={sortBy}
      options={offerSortOptions}
      formatter={formatOfferSortOption.bind(formatOfferSortOption, $t)}
    />
  </label>

  <hr class="divider" />

  <div class="vertical">
    <span typography="label-large">{$t("words.stop_other")}</span>

    <label class="horizontal">
      <input type="checkbox" bind:checked={directOnly} />
      <span typography="body-small">{$t("words.stop_zero")}</span>
    </label>
  </div>
</div>

<style>
  .search-options {
    display: flex;
    flex-flow: column;
    gap: 16px;
    padding: 16px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
    user-select: none;
  }

  .search-options :global(.select-field) {
    --height: 40px;
  }

  .divider {
    margin: 0;
    border: 0;
    border-bottom: var(--color-main-neutral-200) 1px solid;
  }

  .vertical {
    display: flex;
    flex-flow: column;
    gap: 8px;
    align-items: flex-start;
  }

  .horizontal {
    display: flex;
    gap: 8px;
    align-items: center;
  }
</style>
