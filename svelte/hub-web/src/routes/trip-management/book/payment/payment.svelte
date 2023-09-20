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
  import routeConfig from "routeConfig";
  import { browser } from "$app/environment";
  import { onDestroy } from "svelte";
  import { callAction } from "utils/common";
  import { loadStripe, type Stripe, type Appearance, type StripeElements } from "@stripe/stripe-js";
  import { env } from "$env/dynamic/public";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { pollableCall } from "utils/pollable-call";
  import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
  import type { ActionPollReturnType } from "./+page.server";
  import type { SearchDataModel } from "../booking-manager.server";

  export let priceQuote: TripOfferPriceQuoteModel;
  export let paymentIntent: SearchDataModel["paymentIntent"];

  let stripe: Stripe | undefined = undefined;
  let stripeElements: StripeElements | undefined = undefined;
  let stripeContainer: HTMLDivElement | undefined = undefined;

  $: priceQuoteId = priceQuote.id;
  $: clientSecret = paymentIntent?.clientSecret;
  $: if (browser) {
    pollPriceQuote(priceQuoteId).then(updateData);
  }
  $: if (browser && clientSecret) {
    createStripe(clientSecret);
  }

  function updateData(value?: ActionPollReturnType): void {
    if (!value) {
      return;
    }

    paymentIntent = value.paymentIntent;
    priceQuote = value.priceQuote;
  }

  async function createStripe(nextClientSecret: string): Promise<void> {
    stripe = (await loadStripe(env.PUBLIC_STRIPE_KEY ?? "", { locale: "en-GB" })) ?? undefined;

    stripeElements = stripe?.elements({ appearance, clientSecret: nextClientSecret });
    const paymentElement = stripeElements?.create("payment");

    if (stripeContainer) {
      paymentElement?.mount(stripeContainer);
    }
  }

  const { poll: pollPriceQuote, cancel: cancelPolling } = pollableCall({
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    func(_: string) {
      return callAction<ActionPollReturnType>({
        action: routeConfig.routes.tripManagement.routes.book.routes.payment.actions.poll,
        apply: false,
      });
    },
    check(result) {
      if (
        result.type !== "success" ||
        result.data?.priceQuote.status === "unspecified" ||
        result.data?.priceQuote.status === "failed"
      ) {
        return { status: "done" };
      }

      if (result.data?.priceQuote.status === "completed") {
        return { status: "done", data: result.data };
      }

      return { status: "pending" };
    },
    sleepMs: 2000,
  });

  export async function pay(): Promise<boolean> {
    if (paymentIntent?.confirmed) {
      return true;
    }

    if (!(priceQuote.price && stripe && clientSecret && stripeElements)) {
      return false;
    }

    const submitResult = await stripeElements.submit();

    if (submitResult.error) {
      return false;
    }

    const confirmationResult = await stripe.confirmPayment({
      elements: stripeElements,
      clientSecret,
      redirect: "if_required",
    });

    if (confirmationResult.error) {
      return false;
    }

    await callAction({
      action: routeConfig.routes.tripManagement.routes.book.routes.payment.actions.confirmPayment,
    });

    return true;
  }

  onDestroy(cancelPolling);
</script>

<div class="payment">
  <h3 class="typography title-medium bold">Payment method</h3>

  <div
    bind:this={stripeContainer}
    class="stripe-container"
    class:pending={priceQuote.status !== "completed"}
  >
    {#if priceQuote.status !== "completed"}
      <LoadingIcon />
    {/if}
  </div>

  <span class="toc typography body-small">
    By booking your ticket you accept Snowfall’s
    <a href={routeConfig.routes.help.routes.termsAndConditions.root} target="_blank">T&amp;Cs</a>,
    the
    <a href="/">carrier’s conditions of carriage</a>
    and
    <a href={routeConfig.routes.help.routes.privacyPolicy.root} target="_blank">privacy policy</a>.
  </span>
</div>

<style>
  .payment {
    display: flex;
    flex-flow: column;
    gap: 24px;
    padding: 24px 40px;
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .stripe-container.pending {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .toc {
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .toc a {
    color: var(--color-main-primary-600);
    text-decoration: none;
  }
</style>
