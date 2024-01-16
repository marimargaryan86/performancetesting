<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Alert from "components/ui/alert.svelte";
  import integrationInstancesClient from "integration-instances-client";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
  import { onMount } from "svelte";
  import Company from "./company.svelte";
  import type { Markups } from "integration/junction-mobile-api/schemas/markups";
  import type { MaybePromise } from "@sveltejs/kit";
  import { getLocaleData } from "i18n";

  export let booking: TripBooking;
  export let transactionTask: MaybePromise<Transaction | undefined> | undefined;

  const i18n = getLocaleData();

  let markupsTask: Promise<Markups | undefined> | undefined;

  onMount(() => {
    markupsTask = integrationInstancesClient.mobile.orders
      .getMarkups({ orderId: booking.orderId })
      .catch(() => undefined);
  });
</script>

<div class="transaction">
  <h3 typography="title-large" weight="bold">{$i18n.words.transactionInfo}</h3>

  {#await transactionTask}
    <div class="pending">
      <LoadingIcon color="var(--color-main-primary-500)" />
    </div>
  {:then transaction}
    {#if transaction}
      <div class="content">
        <div>
          <span typography="label-large">{$i18n.words.transactionType}</span>
          <strong typography="body-large" weight="bold">
            {$i18n.types[transaction.payment.method]}
          </strong>
        </div>

        <div>
          <span typography="label-large">{$i18n.words.paymentType}</span>
          <strong typography="body-large" weight="bold">
            {$i18n.types[transaction.payment.type]}
          </strong>
        </div>

        <Company
          company={transaction.beneficiary}
          price={booking.price.total}
          breakdownList={booking.price.breakdown}
          title={$i18n.words.provider}
        />

        <Company
          company={transaction.payer}
          price={booking.price.total}
          breakdownList={booking.price.breakdown}
          {markupsTask}
          title={$i18n.words.reseller}
        />
      </div>
    {:else}
      <Alert typography="body-medium" type="warning" dismissable={false}>
        {$i18n.sentences.transactionNotFound}
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
