<script lang="ts">
  import BookingSteps from "../booking-steps.svelte";
  import Button from "components/ui/button.svelte";
  import AgentContactInfo from "./agent-contact-information.svelte";
  import Passengers, { type Passenger } from "./passengers.svelte";
  import Summary from "./summary.svelte";
  import { onMount } from "svelte";
  import type { BookingSearchData } from "../search-form.svelte";
  import OffersMockup from "../offers-mockup";
  import routeConfig from "routeConfig";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import type { OfferModel } from "../select-offer/offer.svelte";

  const currentBookingStep = 3;

  let data: Partial<BookingSearchData> = {};
  let passengers: Partial<Passenger>[] = [];
  let offer: OfferModel | undefined = undefined;
  let fare: OfferModel["alternativeFares"][number] | undefined = undefined;

  onMount(() => {
    const urlParams = $page.url.searchParams;

    data.adults = Number(urlParams.get("adults")) ?? 0;
    data.children = Number(urlParams.get("children")) ?? 0;
    data.infants = Number(urlParams.get("infants")) ?? 0;
    data.origin = urlParams.get("origin") ?? "";
    data.destination = urlParams.get("destination") ?? "";
    data.outbound = new Date(Number(urlParams.get("from"))) ?? undefined;

    offer = OffersMockup.find((item) => item.id === Number(urlParams.get("offer_id")));
    fare = offer?.alternativeFares.find((item) => item.id === Number(urlParams.get("fare_id")));

    for (let i = 1; i <= data.adults; i++) {
      passengers.push({ type: "Adult" });
    }
    for (let i = 1; i <= data.children; i++) {
      passengers.push({ type: "Child" });
    }
    for (let i = 1; i <= data.infants; i++) {
      passengers.push({ type: "Infant" });
    }

    passengers = passengers;
  });

  function goToSelectOfferPage(): void {
    goto(routeConfig.book.select.root + $page.url.search);
  }

  function goToPaymentPage(): void {
    goto(routeConfig.book.payment.root + $page.url.search);
  }
</script>

<svelte:head>
  <title>Summary · Junction Hub</title>
</svelte:head>

<h1 class="typography headline-medium bold container header">Summary</h1>
<BookingSteps currentStep={currentBookingStep} />

<div class="background">
  <div class="page-wrapper container">
    <div class="passengers">
      <Passengers bind:passengers />
      <AgentContactInfo />
    </div>

    {#if offer && fare}
      <Summary {offer} {fare} />
    {/if}
  </div>

  <div class="next-block">
    <Button on:click={goToSelectOfferPage} size="medium" variant="outline">Previous</Button>
    <Button on:click={goToPaymentPage} size="medium"><span class="next-btn">Next</span></Button>
  </div>
</div>

<style>
  .header {
    padding-top: 16px;
  }

  h1 {
    margin-bottom: 16px;
  }

  .container {
    margin: 0 24px;
  }

  .background {
    padding-top: 24px;
    background: var(--color-gradient-booking-flow);
  }

  .page-wrapper {
    position: relative;
    display: flex;
    flex-direction: row;
    gap: 16px;
    align-items: flex-start;
    justify-content: space-between;
    padding-bottom: 24px;
  }

  .passengers {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
  }

  .next-block {
    position: sticky;
    bottom: 0;
    z-index: 100;
    display: flex;
    gap: 16px;
    justify-content: space-between;
    width: 100%;
    padding: 16px 24px;
    background-color: var(--color-common-dark-strong);
  }

  .next-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100px;
  }
</style>
