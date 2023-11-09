<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Alert from "components/ui/alert.svelte";
  import integrationInstancesClient from "integration-instances-client";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
  import { onMount } from "svelte";
  import { capitalize } from "utils/common";
  import Company from "./company.svelte";
  import type { Markups } from "integration/junction-mobile-api/schemas/markups";
  import type { MaybePromise } from "@sveltejs/kit";

  export let booking: TripBooking;
  export let transactionTask: MaybePromise<Transaction | undefined> | undefined;

  let markupsTask: Promise<Markups | undefined> | undefined;

  onMount(() => {
    markupsTask = integrationInstancesClient.mobile.orders
      .getMarkups({ orderId: booking.orderId })
      .catch(() => undefined);
  });
</script>

<div class="transaction">
  <h3 class="typography title-large bold">Transaction info</h3>

  {#await transactionTask}
    <div class="pending">
      <LoadingIcon color="var(--color-main-primary-500)" />
    </div>
  {:then transaction}
    {#if transaction}
      <div class="content">
        <div>
          <span class="typography label-large">Transaction type</span>
          <strong class="typography body-large bold">
            {capitalize(transaction.payment.method)}
          </strong>
        </div>

        <div>
          <span class="typography label-large">Payment type</span>
          <strong class="typography body-large bold">
            {capitalize(transaction.payment.type)}
          </strong>
        </div>

        <Company
          company={transaction.beneficiary}
          price={booking.price.total}
          breakdownList={booking.price.breakdown}
          title="Provider"
        />

        <Company
          company={transaction.payer}
          price={booking.price.total}
          breakdownList={booking.price.breakdown}
          {markupsTask}
          title="Reseller"
        />
      </div>
    {:else}
      <Alert class="typography body-medium" type="warning" dismissable={false}>
        Transaction not found
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
