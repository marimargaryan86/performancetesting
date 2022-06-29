<script lang="ts">
  import utils from "$lib/utils";

  export let week: {
    label: string;
    percentage: number;
    sum: number;
    currency?: string;
  };
</script>

<div
  class="column"
  style:--height="{week.percentage * 100}%"
  style:--padding-top="{100 - week.percentage * 100}%"
>
  {#if week.currency}
    <span class="amount">
      <span>{utils.formatCurrency(week.sum, week.currency)}</span>
      <b />
    </span>
  {/if}

  <span class="bar" />

  <strong>{week.label}</strong>
</div>

<style>
  .column {
    align-items: center;
    display: flex;
    flex-flow: column;
    height: 100%;
    justify-content: flex-end;
    padding-top: var(--padding-top);
  }

  .bar {
    background-color: var(--color-orange-lightest);
    border-radius: 5px;
    display: block;
    height: var(--height);
    margin-bottom: 4px;
    width: 40px;
  }

  .column:hover > .bar {
    background-color: var(--color-orange);
  }

  .column > strong {
    border-top: var(--color-gray-lightest) 1px solid;
    display: block;
    padding-top: 8px;
    text-align: center;
    width: 100%;
  }

  .amount {
    visibility: hidden;
  }

  .column:hover > .amount {
    visibility: visible;
  }

  .amount > span {
    background-color: var(--color-orange);
    border-radius: 2px;
    color: var(--color-white);
    display: block;
    font-size: 8px;
    font-weight: 500;
    margin-bottom: 4px;
    padding: 4px;
    position: relative;
  }

  .amount > span::after {
    border: transparent 0 solid;
    border-top-color: var(--color-orange);
    border-width: 4px 8px 0;
    content: "";
    display: block;
    left: 50%;
    position: absolute;
    top: 100%;
    transform: translateX(-50%);
  }

  .amount > b {
    border-left: var(--color-orange) 2px dotted;
    display: block;
    height: 10px;
    left: calc(50% - 1px);
    margin-bottom: 14px;
    position: relative;
    width: 0;
  }

  .amount > b::after {
    background-color: var(--color-orange);
    border: var(--color-white) 1.5px solid;
    border-radius: 50%;
    box-shadow: 0 0 0 2px var(--color-orange-lightest);
    content: "";
    display: block;
    height: 10px;
    left: 50%;
    position: absolute;
    top: 100%;
    transform: translateX(-50%);
    width: 10px;
  }
</style>
