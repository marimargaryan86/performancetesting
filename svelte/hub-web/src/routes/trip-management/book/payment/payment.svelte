<script lang="ts" context="module">
  import paymentIllustrationImg from "assets/images/payment-illustration.png";

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
  import { callAction } from "utils/common";
  import {
    loadStripe,
    type Stripe,
    type Appearance,
    type StripeElements,
    type StripePaymentElement,
  } from "@stripe/stripe-js";
  import { env } from "$env/dynamic/public";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import type { SearchDataModel } from "../booking-manager.server";
  import Dialog from "components/ui/dialogues/dialog.svelte";
  import Button from "components/ui/button.svelte";

  export let paymentIntent: SearchDataModel["paymentIntent"];

  let dialog: Dialog | undefined = undefined;
  let stripe: Stripe | undefined = undefined;
  let stripeElements: StripeElements | undefined = undefined;
  let stripeContainer: HTMLDivElement | undefined = undefined;
  let error: string | undefined = undefined;
  let paymentElement: StripePaymentElement | undefined = undefined;

  $: if (error) {
    dialog?.open();
  } else {
    dialog?.close();
  }
  $: clientSecret = paymentIntent?.clientSecret;
  $: if (browser && clientSecret) {
    createStripe(clientSecret);
  }
  $: if (browser && paymentElement && stripeContainer) {
    paymentElement.mount(stripeContainer);
  }

  async function createStripe(nextClientSecret: string): Promise<void> {
    stripe = (await loadStripe(env.PUBLIC_STRIPE_KEY ?? "", { locale: "en-GB" })) ?? undefined;
    stripeElements = stripe?.elements({ appearance, clientSecret: nextClientSecret });
    paymentElement = stripeElements?.create("payment");
  }

  export async function pay(): Promise<boolean> {
    error = undefined;

    if (paymentIntent?.confirmed) {
      return true;
    }

    if (!(stripe && clientSecret && stripeElements)) {
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
      error = confirmationResult.error.message;
      return false;
    }

    await callAction({
      action: routeConfig.routes.tripManagement.routes.book.routes.payment.actions.confirmPayment,
    });

    return true;
  }

  function clearError(): void {
    error = undefined;
  }
</script>

<Dialog bind:this={dialog}>
  <div class="dialog">
    <img src={paymentIllustrationImg} alt="" />
    <div>
      <h3 class="typography display-small bold">Payment declined</h3>
      <p class="typography body-medium">{error ?? "An unexpected error occured"}</p>
    </div>
    <Button size="small" on:click={clearError}>Try again</Button>
  </div>
</Dialog>

<div class="payment">
  <span class="typography title-medium bold">Payment method</span>

  <div bind:this={stripeContainer} class="stripe-container" class:pending={!paymentIntent}>
    {#if !paymentIntent}
      <LoadingIcon />
    {/if}
  </div>

  <span class="toc typography body-small">
    By booking your ticket you accept Snowfall’s
    <a href={routeConfig.routes.help.routes.termsAndConditions.root} target="_blank">T&amp;Cs</a>,
    the
    <a href={routeConfig.routes.help.routes.conditionsOfCarriage.root} target="_blank"
      >carrier’s conditions of carriage</a
    >
    and
    <a href={routeConfig.routes.help.routes.privacyPolicy.root} target="_blank">privacy policy</a>.
  </span>
</div>

<style>
  .payment {
    display: flex;
    flex-flow: column;
    gap: 16px;
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

  .dialog {
    display: flex;
    flex-flow: column;
    gap: 32px;
    align-items: center;
    width: 100%;
    max-width: 482px;
    padding: 32px;
  }

  .dialog > div {
    display: flex;
    flex-flow: column;
    gap: 8px;
    text-align: center;
  }

  .dialog > div > p {
    color: var(--color-main-neutral-700);
  }
</style>
