<script lang="ts">
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import Alert from "$lib/components/ui/alert.svelte";
  import integrationInstancesClient from "~/integration-instances-client";
  import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { onMount } from "svelte";
  import Company from "./company.svelte";
  import type { MaybePromise } from "@sveltejs/kit";
  import { getTranslator } from "$lib/i18n";

  export let booking: HubSchemas.TripBooking;
  export let transactionTask: MaybePromise<HubSchemas.Transaction | undefined> | undefined;

  const t = getTranslator();

  let markupsTask: Promise<MobileSchemas.Markups | undefined> | undefined;

  onMount(() => {
    markupsTask = integrationInstancesClient.mobile.orders
      .getMarkups({ orderId: booking.orderId })
      .catch(() => undefined);
  });
</script>

<div class="transaction">
  <h3 typography="title-large" weight="bold">{$t("words.transactionInfo")}</h3>

  {#await transactionTask}
    <div class="pending">
      <LoadingIcon color="var(--color-main-primary-500)" />
    </div>
  {:then transaction}
    {#if transaction}
      <div class="content">
        <div>
          <span typography="label-large">{$t("words.transactionType")}</span>
          <strong typography="body-large" weight="bold">
            {$t(`types.${transaction.payment.method}`)}
          </strong>
        </div>

        <div>
          <span typography="label-large">{$t("words.paymentType")}</span>
          <strong typography="body-large" weight="bold">
            {$t(`types.${transaction.payment.type}`)}
          </strong>
        </div>

        <Company
          company={transaction.beneficiary}
          price={transaction.amounts.beneficiary}
          title={$t("words.provider")}
        />

        <Company
          company={transaction.payer}
          price={transaction.amounts.totalAmount}
          breakdownList={booking.price.breakdown}
          {markupsTask}
          title={$t("words.reseller")}
        />
      </div>
    {:else}
      <Alert typography="body-medium" type="warning" dismissable={false}>
        {$t("sentences.transactionNotFound")}
      </Alert>
    {/if}
  {/await}
</div>

<style>
  .transaction {
    display: flex;
    flex-flow: column;
    gap: 32px;
    width: 100%;
    max-width: 564px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .pending {
    display: flex;
    justify-content: center;
  }

  .content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px 16px;
  }

  .content > div {
    display: flex;
    flex-flow: column;
    gap: 4px;
  }
</style>
