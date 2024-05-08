<script lang="ts" context="module">
  export const ONBOARDING_COOKIE = "onboarding-cookie";

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
  import { browser } from "$app/environment";
  import { env } from "$env/dynamic/public";
  import Icon from "$lib/components/icons/icon.svelte";
  import { getLocale } from "$lib/i18n";
  import routeConfig from "$lib/route-config";
  import { getCookieJar } from "$lib/utils/cookie-jar";
  import {
    loadStripe,
    type Appearance,
    type Stripe,
    type StripeCardElement,
    type StripeElements,
  } from "@stripe/stripe-js";

  const locale = getLocale();

  export let data;

  let stripe: Stripe | undefined;
  let stripeElements: StripeElements | undefined;
  let cardElement: StripeCardElement | undefined;
  let stripeContainer: HTMLDivElement | undefined;
  let error: string | undefined;

  if (browser && !data.completed) {
    createStripe();
  }
  $: if (browser && cardElement && stripeContainer) {
    cardElement.mount(stripeContainer);
  }

  async function createStripe(): Promise<void> {
    stripe = (await loadStripe(env.PUBLIC_STRIPE_KEY ?? "", { locale: $locale })) ?? undefined;
    stripeElements = stripe?.elements({
      locale: $locale,
      appearance,
    });
    cardElement = stripeElements?.create("card", {
      hidePostalCode: true,
    });
  }

  async function submit(): Promise<void> {
    if (!(stripe && cardElement)) {
      return;
    }

    const { setupIntent, error: stripeError } = await stripe.confirmCardSetup(
      data.onboarding.clientSecret,
      {
        /* eslint-disable camelcase */
        payment_method: {
          card: cardElement,
          billing_details: {
            name: data.onboarding.companyName,
          },
        },
        /* eslint-enable camelcase */
      },
    );

    if (setupIntent) {
      getCookieJar().set(ONBOARDING_COOKIE, data.onboarding.id);
      data.completed = true;
    }

    if (stripeError) {
      error = stripeError.message;
    }
  }
</script>

<main>
  <h1 typography="headline-large">Junction Hub Onboarding</h1>
  <h2 typography="headline-small">{data.onboarding.companyName}</h2>
  {#if data.completed}
    <div class="completed">
      <h3 typography="body-large">
        <Icon variant="checked-circular" color="var(--color-main-primary-500)" />
        Credit card successfully added
      </h3>
      <a variant="primary" size="medium" href={routeConfig.root}>Go to home</a>
    </div>
  {:else}
    <form on:submit|preventDefault={submit}>
      <div bind:this={stripeContainer} class="stripe-container" />
      <span class="error" typography="body-medium">{error}</span>
      <button variant="primary" size="medium">Finalize</button>
    </form>
  {/if}
</main>

<style>
  main {
    display: flex;
    flex-flow: column;
    gap: 8px;
    align-items: center;
    justify-content: flex-start;
    width: 100%;
    height: 100vh;
    padding: 32px 0 0;
  }

  .completed {
    display: flex;
    flex-flow: column;
    gap: 16px;
    align-items: center;
  }

  .error {
    color: var(--color-semantic-error-500);
  }

  h2 {
    color: var(--color-main-neutral-700);
  }

  h3 {
    display: flex;
    gap: 8px;
    justify-content: center;
  }

  form {
    display: flex;
    flex-flow: column;
    gap: 16px;
    width: 100%;
    max-width: 800px;
    margin-top: 24px;
  }

  form > button {
    align-self: flex-end;
  }

  .stripe-container {
    width: 100%;
  }
</style>
