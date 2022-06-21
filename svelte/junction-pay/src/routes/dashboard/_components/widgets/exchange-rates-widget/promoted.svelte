<script lang="ts">
  import Button from "$lib/components/ui/button.svelte";
  import GraphIcon from "$lib/icons/graph-icon.svelte";
  import type { Fluctuation } from "$models/pay-models";
  import utils from "$lib/utils";

  let promoted_: Fluctuation;
  export { promoted_ as promoted };

  $: promoted = {
    code: promoted_.code,
    sign: utils.getCurrencySign(promoted_.code),
    amount: Math.abs(promoted_.amount) * 100,
    direction: promoted_.amount < 0 ? "down" : "up",
  };
</script>

<div class="promoted">
  <span class="icon">
    <GraphIcon />
    <span>{promoted.sign}</span>
  </span>

  <strong class="stats">
    {promoted.code} -
    <span class="direction {promoted.direction}">{promoted.amount}% {promoted.direction}</span>
  </strong>
  <Button>Buy now</Button>
</div>

<style>
  .promoted {
    align-items: center;
    background-color: var(--color-orange);
    border-radius: 10px;
    color: var(--color-white);
    display: grid;
    gap: 8px;
    grid-template-columns: max-content 1fr max-content;
    height: 44px;
    padding: 0 15px;
  }

  .promoted > :global(button) {
    background-color: var(--color-white);
    border-radius: 13px;
    color: var(--color-orange);
    font-size: 12px;
    font-weight: 500;
    height: 26px;
    padding: 0 10px;
  }

  .icon {
    position: relative;
  }

  .icon > :global(svg) {
    vertical-align: top;
  }

  .icon > span {
    color: var(--color-orange);
    font-size: 7px;
    left: 6px;
    position: absolute;
    top: 3px;
    transform: translateX(-50%);
  }

  .direction {
    font-weight: 500;
  }

  .direction::before {
    border: transparent 6px solid;
    border-bottom-width: 10px;
    border-top-width: 0;
    content: "";
    display: inline-block;
    margin-right: 5px;
  }

  .direction.up::before {
    border-bottom-color: var(--color-green-light);
  }

  .direction.down::before {
    border-bottom-color: var(--color-red-light);
    transform: rotateZ(180deg);
  }
</style>
