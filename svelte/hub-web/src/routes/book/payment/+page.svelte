<script lang="ts" context="module">
  const appearance: Appearance = {
    theme: "stripe",
    variables: {
      colorPrimary: "#0570de",
      colorBackground: "#ffffff",
      colorText: "#17372f",
      colorDanger: "#db3041",
      fontFamily: "Inter, Open Sans, system-ui, sans-serif",
      spacingUnit: "6px",
      borderRadius: "4px",
    },
    rules: {
      ".Error": {
        fontSize: "12px",
      },
      ".Label": {
        fontSize: "14px",
        fontWeight: "600",
      },
      ".Input:focus": {
        border: "1px solid #bcc2bd",
        boxShadow: "none",
      },
      ".Input": {
        border: "1px solid #d7dbd8",
        fontSize: "14px",
        borderRadius: "8px",
        padding: "10px 16px",
        boxShadow: "none",
      },
    },
  };
</script>

<script lang="ts">
  import Button from "components/ui/button.svelte";
  import Countdown from "../countdown.svelte";
  import Summary from "../summary.svelte";
  import routeConfig from "routeConfig";
  import Checkbox from "components/ui/checkbox.svelte";
  import { browser } from "$app/environment";
  import { page } from "$app/stores";
  import { onDestroy } from "svelte";
  import { callAction, sleep } from "utils/common";
  import { loadStripe, type Stripe, type Appearance, type StripeElements } from "@stripe/stripe-js";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";
  import type { ActionPollReturnType } from "./+page.server";
  import { URLExtended } from "utils/url";

  export let data;

  let priceQuoteId: string | undefined = data.priceQuote.id;
  let stripe: Stripe | undefined = undefined;
  let stripeElements: StripeElements | undefined = undefined;
  let stripeContainer: HTMLDivElement | undefined = undefined;
  let termsAccepted = false;

  $: clientSecret = data.searchData.paymentIntent?.clientSecret;
  $: backUrl = getBackUrl(data.searchData);
  $: priceQuoteId = data.priceQuote.id;
  $: if (browser && priceQuoteId) {
    pollPriceQuote(priceQuoteId);
  }
  $: if (browser && clientSecret) {
    createStripe(clientSecret);
  }

  async function createStripe(nextClientSecret: string): Promise<void> {
    stripe = (await loadStripe(env.PUBLIC_STRIPE_KEY ?? "", { locale: "en-GB" })) ?? undefined;

    stripeElements = stripe?.elements({ appearance, clientSecret: nextClientSecret });
    const paymentElement = stripeElements?.create("payment");

    if (stripeContainer) {
      paymentElement?.mount(stripeContainer);
    }
  }

  function getBackUrl(searchData: typeof data.searchData): URL {
    return new URLExtended(routeConfig.book.select.root, {
      base: $page.url.origin,
      query: {
        origin: searchData.origin.id,
        destination: searchData.destination.id,
        adults: searchData.passengers.adults.toString(),
        children: searchData.passengers.children.toString(),
        infants: searchData.passengers.infants.toString(),
        outbound: searchData.departureAfter.toLocaleDateString("sv-SE"),
      },
    });
  }

  async function pollPriceQuote(id: string): Promise<void> {
    if (priceQuoteId !== id) {
      return undefined;
    }

    if (data.priceQuote.status === "completed") {
      return;
    }

    const result = await callAction<ActionPollReturnType>({
      action: routeConfig.book.payment.actions.poll,
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
      data.priceQuote = result.data.priceQuote;
      data.searchData.paymentIntent = result.data.paymentIntent;

      return;
    }

    await sleep(2000);

    return pollPriceQuote(id);
  }

  async function pay(): Promise<void> {
    if (!data.priceQuote.price || !stripe || !clientSecret || !stripeElements) {
      return;
    }

    const result = await stripeElements.submit();

    if (result.error) {
      return;
    }

    await stripe.confirmPayment({
      elements: stripeElements,
      clientSecret,
      redirect: "if_required",
    });

    goto(routeConfig.book.passengerDetails.root);
  }

  onDestroy(() => {
    priceQuoteId = undefined;
  });
</script>

<svelte:head>
  <title>Payment · Book · Junction Hub</title>
</svelte:head>

<div class="content">
  <Countdown expiresAt={data.priceQuote.expiresAt} show />

  <div class="scroll">
    <div class="details">
      <div bind:this={stripeContainer} class="stripe-container" />

      <label for="toc" class="toc typography body-small">
        <Checkbox id="toc" bind:checked={termsAccepted} />
        <span>
          By booking your ticket you accept Snowfall’s
          <a href="/">T&amp;Cs</a>, the <a href="/">carrier’s conditions of carriage</a>
          and
          <a href="/">privacy policy</a>.
        </span>
      </label>
    </div>

    <Summary passengers={[]} />
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <Button size="small" variant="text" href={backUrl.toString()}>Previous</Button>
    <Button size="small" on:click={pay} disabled={!termsAccepted}>Next</Button>
  </div>
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    width: 100%;
    padding-top: 24px;
    overflow: auto;
  }

  .content > :global(.countdown) {
    max-width: 1104px;
    margin: 0 24px 24px;
  }

  .scroll {
    --summary-width: 320px;
    --passengers-width: calc(1152px - var(--summary-width) - 72px);

    display: flex;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    padding: 0 24px 24px;
    overflow: auto;
  }

  .scroll > .details {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-self: flex-start;
    width: 100%;
    max-width: var(--passengers-width);
  }

  .stripe-container {
    padding: 40px 80px;
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .scroll > :global(.summary) {
    position: sticky;
    top: 0;
    left: 0;
    flex-shrink: 0;
    width: var(--summary-width);
  }

  .toc {
    display: flex;
    gap: 12px;
    padding: 40px 80px;
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .toc > :global(.checkbox) {
    cursor: pointer;
  }

  .toc a {
    color: var(--color-main-primary-600);
    text-decoration: none;
  }

  .actions {
    position: relative;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
  }

  .actions > .wrapper {
    display: flex;
    gap: 16px;
    justify-content: space-between;
    width: 100%;
    max-width: 1104px;
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

  .actions > .wrapper > :global(button) {
    width: 140px;
  }
</style>
