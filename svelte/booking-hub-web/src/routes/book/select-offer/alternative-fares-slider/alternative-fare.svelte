<script lang="ts">
  import Button from "components/ui/button.svelte";
  import FareRule from "./fare-rules/fare-rule.svelte";
  import CheckCircleIcon from "components/icons/check-circle-icon.svelte";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let alternativeFare;
  export let selected = false;

  function toggleSelectedFare(): void {
    dispatch("toggleSelectedFare", {
      id: alternativeFare.id,
    });
  }
</script>

<div class="alternative-fare">
  <div class="type typography body-small">{alternativeFare.type}</div>
  <h3 class="title">{alternativeFare.title}</h3>
  <div class="description">
    <div class="fare-description typography body-x-small">{alternativeFare.description}</div>
    <FareRule fareRule={alternativeFare.description} />
  </div>
  <div class="price-wrapper">
    <span class="type typography body-small">From</span>
    <span class="price typography body-medium-weight-600">€{alternativeFare.price}</span>
  </div>
  {#if selected}
    <Button size="x-small" on:click={toggleSelectedFare}>
      <span class="button-content typography body-small-weight-600">
        <CheckCircleIcon />
        Select
      </span>
    </Button>
  {:else}
    <Button on:click={toggleSelectedFare} size="x-small" variant="outline">
      <span class="typography body-small-weight-600"> Select </span>
    </Button>
  {/if}
</div>

<style>
  .alternative-fare {
    position: relative;
    display: flex;
    flex-direction: column;
    min-width: 160px;
    padding: 16px;
    background-color: var(--color-main-primary-50);
    border-radius: 16px;
  }

  .type {
    color: #829792;
  }

  .title {
    margin-bottom: 16px;
    color: var(--color-main-primary-700);
    font-weight: 600;
    font-size: 18px;
    line-height: 28px;
  }

  .fare-description {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .description {
    margin-bottom: 18px;
  }

  .price-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0 8px;
    border-top: 1px solid #bfd0cc;
  }

  .price {
    color: var(--color-main-primary-900);
  }

  .button-content {
    display: flex;
    gap: 8px;
    justify-content: center;
  }
</style>
