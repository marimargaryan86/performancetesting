<script lang="ts">
  import { browser } from "$app/environment";
  import { invalidateAll } from "$app/navigation";
  import { manager } from "$lib/booking-manager/booking-manager";
  import { carSearchDataParser } from "$lib/components/pages/trip-management/book/search/car-search-data";
  import CollapsibleCarSearch from "$lib/components/pages/trip-management/book/search/car-components/collapsible-car-search.svelte";
  import OfferResultLayout from "$lib/components/pages/trip-management/offer-result-layout.svelte";
  import Alert from "$lib/components/ui/alert.svelte";
  import { getTranslator } from "$lib/i18n";
  import routeConfig from "$lib/route-config";
  import { onDestroy, type ComponentEvents } from "svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import type { PageData } from "./$types";

  const t = getTranslator();

  export let data: PageData;

  $: searchData = carSearchDataParser.fromSearchData(data.bookingSession.searchData);

  let offers: MobileSchemas.Offer[] = [];
  let offerPollController: AbortController | undefined;
  let offersPending = true;

  $: offerSearchId = data.bookingSession.offerSearch.id;
  $: getOffers(offerSearchId);

  async function getOffers(nextOfferSearchId: string): Promise<void> {
    if (!browser) {
      return;
    }

    offers = [];
    offerPollController?.abort();
    offerPollController = new AbortController();

    for await (const offer of manager.getOffers(nextOfferSearchId, offerPollController.signal)) {
      offers = [...offers, offer];
    }

    offersPending = false;
  }

  async function search(event: ComponentEvents<CollapsibleCarSearch>["search"]): Promise<void> {
    event.detail.pending.set(true);
    offers = [];
    offersPending = true;
    await manager.search(event.detail.data, false);
    await invalidateAll();
    event.detail.pending.set(false);
  }

  onDestroy(() => {
    if (browser) {
      offerPollController?.abort();
    }
  });
</script>

<OfferResultLayout
  pageTitle={$t("pages.tripManagement.pages.book.pages.car.pages.select.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.car.pages.select.subTitle")}
  showActions
  expiresAt={data.bookingSession.offerSearch.expiresAt}
  showCountdown={Boolean(offers.length)}
>
  <CollapsibleCarSearch {searchData} on:search={search} slot="search-drawer" />

  <span slot="search-options">TODO: Search options</span>

  <ul class="offer-result">
    {#each offers as offer}
      <li>{offer.id}</li>
    {/each}

    {#if offersPending}
      <li>Loading...</li>
      <li>Loading...</li>
      <li>Loading...</li>
      <li>Loading...</li>
    {:else if !offers.length}
      <li>
        <Alert type="warning" dismissable={false}>
          <span typography="body-medium">{$t("sentences.noTripsFound")}</span>
        </Alert>
      </li>
    {/if}
  </ul>

  <svelte:fragment slot="actions">
    <a
      variant="primary"
      size="small"
      class="action"
      href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.payment.root}
    >
      Next
    </a>
  </svelte:fragment>
</OfferResultLayout>

<style>
  .offer-result {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-self: flex-start;
    width: 100%;
    max-width: var(--result-width);
  }

  a.action {
    width: 140px;
  }
</style>
