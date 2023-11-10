<script lang="ts">
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import RefundDialog from "./refund-dialog.svelte";
  import Transaction from "./transaction.svelte";
  import { permitted } from "utils/permissions";
  import userStore from "stores/user-store";
  import type { Transaction as TransactionModel } from "integration/junction-hub-api/schemas/transaction";
  import { onMount } from "svelte";
  import integrationInstancesClient from "integration-instances-client";
  import type { MaybePromise } from "@sveltejs/kit";

  export let booking: TripBooking;

  let transactionTask: MaybePromise<TransactionModel | undefined> | undefined;

  onMount(() => {
    if (booking.transactionId) {
      transactionTask =
        booking.transaction ??
        integrationInstancesClient.hub.transactions.get({ id: booking.transactionId });
    }
  });
</script>

<div class="admin">
  <Transaction {booking} {transactionTask} />

  {#if booking.cancellation && permitted($userStore, "refund", "*")}
    {#await transactionTask then transaction}
      {#if transaction && !booking.refund}
        <RefundDialog bind:booking {transaction} />
      {/if}
    {/await}
  {/if}
</div>

<style>
  .admin {
    display: flex;
    flex-flow: column;
    gap: 24px;
  }
</style>
