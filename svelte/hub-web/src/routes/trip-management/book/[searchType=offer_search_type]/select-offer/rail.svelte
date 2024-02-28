<script lang="ts">
  import { onDestroy, type ComponentEvents } from "svelte";
  import type { PageData } from "./$types";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { browser } from "$app/environment";
  import {
    manager,
    type PartialSelectedOffer,
    type SearchData,
  } from "$lib/booking-manager/booking-manager";
  import OfferResultLayout from "$lib/components/pages/trip-management/offer-result-layout.svelte";
  import { getTranslator } from "$lib/i18n";
  import CollapsibleTripSearch from "$lib/components/pages/trip-management/book/search/rail-components/collapsible-trip-search.svelte";
  import {
    SEARCH_WINDOW_H,
    tripSearchDataParser,
  } from "$lib/components/pages/trip-management/book/search/trip-search-data";
  import { goto, invalidateAll } from "$app/navigation";
  import { Feature, getFeatureTools } from "$lib/utils/feature-flags";
  import OfferList from "$lib/components/pages/trip-management/book/select-offer/rail-components/offer-list.svelte";
  import type { TripDirection } from "$lib/models/trip";
  import Checkout from "$lib/components/pages/trip-management/book/select-offer/rail-components/checkout.svelte";
  import { ensureDefined } from "$lib/utils/array";
  import routeConfig from "$lib/route-config";
  import SearchOptions from "$lib/components/pages/trip-management/book/select-offer/rail-components/search-options.svelte";
  import { getOfferSortFunc, type OfferSortOption } from "$lib/sorting/offer";
  import { getOfferFilterFunc } from "$lib/filters/offer";

  const featureTools = getFeatureTools();
  const t = getTranslator();

  export let data: PageData;

  let offers: MobileSchemas.Offer[] = [];
  let pollOffersController: AbortController | undefined;
  let offersPending = true;
  let selected: PartialSelectedOffer = { ...(data.bookingSession.selectedOffer ?? {}) };
  let createPriceQuotePending = false;
  let tripDirection: TripDirection = "outbound";
  let sortBy: OfferSortOption = "earliest-departure";
  let directOnly = false;

  $: searchData = tripSearchDataParser.fromSearchData(data.bookingSession.searchData);
  $: offerSearchId = data.bookingSession.offerSearch.id;
  $: if (browser) {
    getOffers(offerSearchId);
  }

  async function getOffers(id: string): Promise<void> {
    offers = [];
    pollOffersController?.abort();
    pollOffersController = new AbortController();
    let currPollOffersController = pollOffersController;

    try {
      offersPending = true;
      for await (const offer of manager.getOffers(id, pollOffersController.signal)) {
        offers = [...offers, offer];
      }
    } finally {
      if (currPollOffersController === pollOffersController) {
        offersPending = false;
      }
    }
  }

  async function searchAux(nextSearchData: SearchData): Promise<void> {
    await manager.search(nextSearchData, $featureTools.hasFeature(Feature.OFFERS_TIME_WINDOWS));
    offers = [];
    offersPending = true;
    selected = {};
    tripDirection = "outbound";
    await invalidateAll();
  }

  async function search(event: ComponentEvents<CollapsibleTripSearch>["search"]): Promise<void> {
    event.detail.pending.set(true);
    await searchAux(event.detail.data);
    event.detail.pending.set(false);
  }

  async function createPriceQuote(
    event: ComponentEvents<Checkout | OfferList>["createpricequote"],
  ): Promise<void> {
    if (createPriceQuotePending) {
      return;
    }

    let offer: MobileSchemas.Offer | undefined;
    let outbound: MobileSchemas.OfferOption | undefined;
    let inbound: MobileSchemas.OfferOption | undefined;

    if ("offerId" in event.detail) {
      const { offerId, outboundId, inboundId } = event.detail;
      offer = offers.find((item) => item.id === offerId);
      outbound = offer?.groups[0]?.options.find((option) => option.id === outboundId);
      inbound = offer?.groups[1]?.options.find((option) => option.id === inboundId);
    } else {
      ({ offer, inbound, outbound } = event.detail);
    }

    if (!(offer && outbound)) {
      return;
    }

    if (searchData.tripType === "round-trip" && !inbound) {
      return;
    }

    try {
      event.detail.pending.set(true);
      createPriceQuotePending = true;

      await manager.selectOffer(
        data.bookingSession,
        offer,
        [outbound, inbound].filter(ensureDefined),
      );
      await goto(routeConfig.routes.tripManagement.routes.book.routes.rail.routes.payment.root);
    } finally {
      event.detail.pending.set(false);
      createPriceQuotePending = false;
    }
  }

  function changeDirection(event: ComponentEvents<Checkout>["changedirection"]): void {
    tripDirection = event.detail;
  }

  function moveTimeWindow(event: ComponentEvents<OfferList>["movetimewindow"]): void {
    const delta = event.detail === "earlier" ? -SEARCH_WINDOW_H : SEARCH_WINDOW_H;

    let nextData: Partial<SearchData> | undefined;

    if (tripDirection === "outbound") {
      const outbound = new Date(data.bookingSession.searchData.outbound);
      outbound.setHours(outbound.getHours() + delta);
      nextData = { outbound };
    } else if (data.bookingSession.searchData.inbound) {
      const inbound = new Date(data.bookingSession.searchData.inbound);
      inbound.setHours(inbound.getHours() + delta);
      nextData = { inbound };
    }

    searchAux({ ...data.bookingSession.searchData, ...nextData });
  }

  onDestroy(() => {
    if (browser) {
      pollOffersController?.abort();
    }
  });
</script>

<OfferResultLayout
  showActions
  pageTitle={$t("pages.tripManagement.pages.book.pages.rail.pages.select.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.rail.pages.select.subTitle")}
  expiresAt={data.bookingSession.offerSearch.expiresAt}
  showCountdown={Boolean(offers.length)}
>
  <CollapsibleTripSearch {searchData} on:search={search} slot="search-drawer" />

  <SearchOptions slot="search-options" bind:sortBy bind:directOnly />

  {#key tripDirection}
    <OfferList
      {offers}
      sort={getOfferSortFunc(sortBy)}
      filter={getOfferFilterFunc(directOnly)}
      pending={offersPending}
      tripType={searchData.tripType}
      tripDate={searchData.tripType === "round-trip" && tripDirection === "inbound"
        ? searchData.inbound
        : searchData.outbound}
      bind:selected
      bind:tripDirection
      on:createpricequote={createPriceQuote}
      on:movetimewindow={moveTimeWindow}
    />
  {/key}

  <Checkout
    {offers}
    {selected}
    {tripDirection}
    tripType={searchData.tripType}
    slot="actions"
    on:createpricequote={createPriceQuote}
    on:changedirection={changeDirection}
  />
</OfferResultLayout>
