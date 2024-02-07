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

  function getCustomerOptions(paymentIntent: PaymentIntent): CustomerOptions | undefined {
    return paymentIntent?.customerId && paymentIntent.ephemeralKey
      ? {
          customer: paymentIntent.customerId,
          ephemeralKey: paymentIntent.ephemeralKey,
        }
      : undefined;
  }
</script>

<script lang="ts">
  import routeConfig from "~/route-config";
  import { browser } from "$app/environment";
  import {
    loadStripe,
    type Stripe,
    type Appearance,
    type StripeElements,
    type StripePaymentElement,
    type CustomerOptions,
  } from "@stripe/stripe-js";
  import { env } from "$env/dynamic/public";
  import LoadingIcon from "~/components/icons/loading-icon.svelte";
  import Dialog from "~/components/ui/dialogues/dialog.svelte";
  import { getLocale, getTranslator } from "~/i18n";
  import type { PaymentIntent } from "../../booking-flow";
  import { getUser } from "~/utils/permissions";

  export let paymentIntent: PaymentIntent | undefined;

  const locale = getLocale();
  const t = getTranslator();
  const user = getUser();

  let dialog: Dialog | undefined;
  let stripe: Stripe | undefined;
  let stripeElements: StripeElements | undefined;
  let stripeContainer: HTMLDivElement | undefined;
  let error: string | undefined;
  let paymentElement: StripePaymentElement | undefined;

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
  $: stripeElements?.update({ locale: $locale });

  async function createStripe(nextClientSecret: string): Promise<void> {
    stripe = (await loadStripe(env.PUBLIC_STRIPE_KEY ?? "", { locale: $locale })) ?? undefined;
    stripeElements = stripe?.elements({
      locale: $locale,
      appearance,
      clientSecret: nextClientSecret,
      customerOptions: paymentIntent ? getCustomerOptions(paymentIntent) : undefined,
    });
    paymentElement = stripeElements?.create("payment", {
      readOnly: paymentIntent?.confirmed,
      defaultValues: {
        billingDetails: {
          email: $user.email,
        },
      },
    });
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

    paymentElement?.update({ readOnly: true });

    return true;
  }

  function clearError(): void {
    error = undefined;
  }
</script>

<Dialog bind:this={dialog}>
  <div class="dialog">
    <img src="/images/illustrations/payment.png" alt="" />
    <div>
      <h3 typography="display-small" weight="bold">{$t("sentences.paymentDeclined")}</h3>
      <p typography="body-medium">{error ?? $t("sentences.anUnexpectedErrorOccurred")}</p>
    </div>
    <button variant="primary" size="small" on:click={clearError}>{$t("actions.tryAgain")}</button>
  </div>
</Dialog>

<div class="payment">
  <span typography="title-medium" weight="bold">{$t("words.paymentMethod")}</span>

  <div bind:this={stripeContainer} class="stripe-container" class:pending={!paymentIntent}>
    {#if !paymentIntent}
      <LoadingIcon />
    {/if}
  </div>

  <span class="toc" typography="body-small">
    {#each $t("sentences.paymentInfo", { returnObjects: true }) as item}
      {#if item.type === "text"}
        {item.value}
      {:else if item.type === "toc"}
        <a href={routeConfig.routes.help.routes.termsAndConditions.root} target="_blank">
          {item.value}
        </a>
      {:else if item.type === "coc"}
        <a href={routeConfig.routes.help.routes.conditionsOfCarriage.root} target="_blank">
          {item.value}
        </a>
      {:else if item.type === "privacy"}
        <a href={routeConfig.routes.help.routes.privacyPolicy.root} target="_blank">
          {item.value}
        </a>
      {/if}
    {/each}
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
