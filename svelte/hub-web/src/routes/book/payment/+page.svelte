<script lang="ts">
  import Summary from "../passenger-details/summary.svelte";
  import TextField from "components/ui/text-field.svelte";
  import RadioIcon from "components/icons/radio-icon.svelte";
  import CreditCardIcon from "components/icons/credit-card-icon.svelte";
  import { loadStripe, type Appearance, type Stripe, type StripeElements } from "@stripe/stripe-js";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import Button from "components/ui/button.svelte";
  import PaymentModal from "./payment-modal.svelte";
  import BillingAddress, { type BillingAddressModel } from "./billing-address.svelte";
  import routeConfig from "routeConfig";
  import { env } from "$env/dynamic/public";
  import type { OfferGroupModel, OfferModel } from "models/booking/offer";

  let offer: OfferModel | undefined = undefined;
  let fare: OfferGroupModel | undefined = undefined;
  let paymentProcessing = false;
  let stripeErrorMessage: string | undefined = undefined;
  let paymentFormElement: HTMLFormElement | undefined;
  let stripeFormElements: StripeElements | undefined = undefined;
  let stripe: Stripe | null = null;

  let billingAddress: BillingAddressModel = {
    addressLine1: undefined,
    addressLine2: undefined,
    townOrCity: undefined,
    country: undefined,
    postcode: undefined,
  };

  $: payDisabled = Boolean(
    !billingAddress.addressLine1 ||
      !billingAddress.townOrCity ||
      !billingAddress.country ||
      !billingAddress.postcode,
  );

  const appearance: Appearance = {
    theme: "stripe",
    variables: {
      colorPrimary: "#0570de",
      colorBackground: "#ffffff",
      colorText: "#17372F",
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
        border: "1px solid #D7DBD8",
        fontSize: "14px",
        borderRadius: "8px",
        padding: "10px 16px",
        boxShadow: "none",
      },
    },
  };

  onMount(async () => {
    if (env.PUBLIC_STRIPE_KEY) {
      stripe = await loadStripe(env.PUBLIC_STRIPE_KEY);
    }

    if (stripe) {
      renderForm();
    }
  });

  const renderForm = (): void => {
    const paymentIntentClientSecret =
      "pi_3NckxhBoi5kRFYub0YHx609g_secret_XLyhA1PwKfwDMBz6Z2LTIrMUr";

    if (paymentIntentClientSecret) {
      stripeFormElements = stripe?.elements({
        clientSecret: paymentIntentClientSecret,
        appearance,
      });
      const paymentElement = stripeFormElements?.create("payment");
      paymentElement?.mount("#payment-element");
    }
  };

  async function purchase(): Promise<void> {
    if (paymentFormElement && stripe) {
      paymentProcessing = true;
      if (stripeFormElements) {
        const returnUrl = new URL(routeConfig.book.confirmation.root, $page.url.href);
        const { error } = await stripe.confirmPayment({
          elements: stripeFormElements,
          confirmParams: {
            // eslint-disable-next-line camelcase
            return_url: returnUrl.toString(),
          },
        });
        if (error) {
          stripeErrorMessage = error.message;
        } else {
          // Your customer will be redirected to your `return_url`. For some payment
          // methods like iDEAL, your customer will be redirected to an intermediate
          // site first to authorize the payment, then redirected to the `return_url`.
        }
      }
    }
  }

  function goToPassengerDetailsPage(): void {
    const url = new URL(routeConfig.book.passengerDetails.root, $page.url.href);
    goto(url);
  }

  function closePaymentModal(): void {
    paymentProcessing = false;
    stripeErrorMessage = undefined;
  }
</script>

<svelte:head>
  <title>Payment · Junction Hub</title>
</svelte:head>

<h1 class="typography headline-medium bold container header">Payment</h1>

<div class="background">
  <div class="page-wrapper container">
    <div class="forms">
      <div class="card-form">
        <h3>Payment method</h3>
        <div class="pay-card">
          <TextField readonly value="Credit Card" />
          <RadioIcon color="var(--color-main-primary-500)" />
          <div class="card-icon">
            <CreditCardIcon />
          </div>
        </div>
        <form
          bind:this={paymentFormElement}
          on:submit={purchase}
          id="payment-form"
          class="payment-form"
        >
          <div id="payment-element" />
        </form>
      </div>
      <BillingAddress bind:billingAddress />
    </div>

    {#if offer && fare}
      <Summary passengers={[]} />
    {/if}
  </div>

  <div class="next-block">
    <Button on:click={goToPassengerDetailsPage} size="medium" variant="outline">Previous</Button>
    <Button form="payment-form" type="submit" disabled={payDisabled} size="medium"
      ><span class="next-btn">Pay</span></Button
    >
  </div>
</div>
<PaymentModal on:close={closePaymentModal} {paymentProcessing} {stripeErrorMessage} />

<style>
  h3 {
    margin-bottom: 16px;
    font-weight: 600;
    font-size: 22px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
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

  .container {
    margin: 0 24px;
  }

  .header {
    padding-top: 16px;
  }

  .card-form {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 100%;
    padding: 40px 80px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .forms {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
    padding-bottom: 60px;
  }

  .forms :global(.text-field) {
    width: 100%;
  }

  .forms :global(.select-field) {
    width: 100%;
  }

  .forms :global(.text-field .wrapper) {
    height: 40px;
  }

  .forms :global(.select-field .wrapper) {
    height: 40px;
  }

  .forms :global(.select-field label) {
    color: var(--color-common-light-strong);
    font-weight: 600;
    font-size: 14px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .forms :global(.text-field label) {
    color: var(--color-common-light-strong);
    font-weight: 600;
    font-size: 14px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .pay-card {
    position: relative;
    width: 50%;
    min-width: 165px;
  }

  .pay-card > :global(svg) {
    position: absolute;
    top: 10px;
    left: 16px;
  }

  .pay-card .card-icon :global(svg) {
    position: absolute;
    top: 8px;
    right: 16px;
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

  .pay-card :global(input) {
    padding-right: 52px;
    padding-left: 52px;
  }
</style>
