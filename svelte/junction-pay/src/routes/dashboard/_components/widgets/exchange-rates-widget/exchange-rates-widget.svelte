<script lang="ts">
  import Button from "$lib/components/ui/button.svelte";
  import routeConfig from "$lib/route-config";
  import type { Fluctuation, Rate } from "$models/pay-models";
  import WidgetHeader from "../widget-header.svelte";
  import Promoted from "./promoted.svelte";

  export let promoted: Fluctuation | undefined = undefined;
  export let rates: Rate[] = [];

  function getDirection(amount: number): string {
    return amount < 0 ? "down" : "up";
  }
</script>

<div class="exchange-rates-widget">
  <WidgetHeader viewMoreUrl={routeConfig.exchangeRates}>FX rates</WidgetHeader>

  {#if promoted}
    <Promoted {promoted} />
  {/if}

  <table>
    <thead>
      <tr>
        <th>Currency</th>
        <th>Live rate</th>
        <th>Yesterday</th>
        <th>Last week</th>
      </tr>
    </thead>

    <tbody>
      {#each rates as rate}
        <tr>
          <td class="country">
            <img src="/images/currency-flags/{rate.code.toLowerCase()}.png" alt="" />
            <span>{rate.code}</span>
          </td>

          <td class="live direction {getDirection(rate.live)}">{Math.abs(rate.live)}</td>
          <td class="past direction {getDirection(rate.yesterday)}">{Math.abs(rate.yesterday)}</td>
          <td class="past direction {getDirection(rate.lastWeek)}">{Math.abs(rate.lastWeek)}</td>
        </tr>
      {/each}

      <tr>
        <td colspan="4" class="show-more">
          <Button><span /></Button>
        </td>
      </tr>
    </tbody>
  </table>
</div>

<style>
  table {
    background-color: var(--color-white);
    border-radius: 10px;
    box-shadow: 0 -11.6375px 37.3625px rgb(0 0 0 / 3%);
    text-align: left;
    width: 100%;
  }

  thead {
    position: relative;
  }

  thead::after {
    border-bottom: var(--color-gray-lightest) 1px solid;
    content: "";
    display: block;
    left: 20px;
    position: absolute;
    width: calc(100% - 40px);
  }

  tbody {
    font-size: 11px;
  }

  th,
  td {
    padding: 13px;
  }

  th {
    padding-top: 23px;
  }

  th:first-child,
  td:first-child {
    padding-left: 20px;
  }

  th:last-child,
  td:last-child {
    padding-right: 20px;
  }

  .country {
    color: var(--color-gray-lighter);
  }

  .country > img {
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 2px;
    height: 19px;
    margin-right: 6px;
    object-fit: cover;
    vertical-align: middle;
    width: 29px;
  }

  .show-more {
    padding: 8px 16px 16px;
    text-align: center;
  }

  .show-more > :global(button) {
    background-color: var(--color-orange);
    height: 33px;
    padding: 0;
    width: 49px;
  }

  .show-more > :global(button::after) {
    border: #ffffff solid;
    border-width: 0 2px 2px 0;
    content: "";
    display: inline-block;
    height: 10px;
    transform: translateY(-2px) rotateZ(45deg);
    width: 10px;
  }

  .live {
    color: var(--color-gray-darker);
  }

  .past {
    color: var(--color-gray-lighter);
  }

  .direction::before {
    border: transparent 6px solid;
    border-bottom-width: 10px;
    border-top-width: 0;
    content: "";
    display: inline-block;
    margin-right: 4px;
  }

  .direction.up::before {
    border-bottom-color: var(--color-green-light);
  }

  .direction.down::before {
    border-bottom-color: var(--color-red-light);
    transform: rotateZ(180deg);
  }

  .exchange-rates-widget > :global(.promoted) {
    margin-bottom: 12px;
  }
</style>
