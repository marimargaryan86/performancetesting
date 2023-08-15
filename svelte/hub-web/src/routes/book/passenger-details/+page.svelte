<script lang="ts">
  import { browser } from "$app/environment";
  import { page } from "$app/stores";
  import type { MaybePromise } from "@sveltejs/kit";
  import Button from "components/ui/button.svelte";
  import type { OfferPriceQuoteModel } from "models/booking/offer";
  import routeConfig from "routeConfig";
  import { onDestroy } from "svelte";
  import { callAction, sleep } from "utils/common";
  import Countdown from "../countdown.svelte";

  export let data;

  let getPriceQuoteTask: MaybePromise<OfferPriceQuoteModel | undefined> = data.priceQuote;
  let priceQuoteId: string | undefined = data.priceQuote.id;

  $: backUrl = getBackUrl(data.searchData);
  $: priceQuoteId = data.priceQuote.id;
  $: if (browser && priceQuoteId) {
    getPriceQuoteTask = pollPriceQuote(priceQuoteId);
  }

  function getBackUrl(searchData: typeof data.searchData): URL {
    const url = new URL(routeConfig.book.select.root, $page.url.origin);
    url.searchParams.set("origin", searchData.origin.id);
    url.searchParams.set("destination", searchData.destination.id);
    url.searchParams.set("adults", searchData.passengers.adults.toString());
    url.searchParams.set("children", searchData.passengers.children.toString());
    url.searchParams.set("infants", searchData.passengers.infants.toString());
    url.searchParams.set("outbound", searchData.departureAfter.toLocaleDateString("sv-SE"));

    return url;
  }

  async function pollPriceQuote(id: string): Promise<OfferPriceQuoteModel | undefined> {
    if (priceQuoteId !== id) {
      return undefined;
    }

    const result = await callAction<{ priceQuote: OfferPriceQuoteModel }>({
      action: routeConfig.book.passengerDetails.actions.poll,
      apply: false,
    });

    if (result.type !== "success") {
      return undefined;
    }

    if (
      result.data?.priceQuote.status === "unspecified" ||
      result.data?.priceQuote.status === "failed"
    ) {
      return undefined;
    }

    if (result.data?.priceQuote.status === "completed") {
      return result.data.priceQuote;
    }

    await sleep(2000);

    return pollPriceQuote(id);
  }

  onDestroy(() => {
    priceQuoteId = undefined;
  });
</script>

<svelte:head>
  <title>Summary · Book · Junction Hub</title>
</svelte:head>

<div class="content">
  <Countdown expiresAt={data.priceQuote.expiresAt} show />

  <div>{data.searchData.origin.name} - {data.searchData.destination.name}</div>
  <div>{data.searchData.departureAfter}</div>
  <div>
    {#await getPriceQuoteTask}
      Loading price quote...
    {:then priceQuote}
      {JSON.stringify(priceQuote)}
    {/await}
  </div>
</div>

<div class="actions">
  <Button size="small" variant="outline" href={backUrl.toString()}>Previous</Button>
  <Button size="small"><span class="next-btn">Next</span></Button>
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    height: 100%;
    padding: 24px;
    overflow: auto;
  }

  .actions {
    display: flex;
    gap: 16px;
    justify-content: space-between;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
  }

  .actions::after {
    position: absolute;
    bottom: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(0deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }

  .actions > :global(button) {
    width: 140px;
  }
</style>
