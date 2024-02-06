<script lang="ts">
  import type { TripBooking } from "~/integration/junction-hub-api/schemas/booking";
  import RefundDialog from "./refund-dialog.svelte";
  import Transaction from "./transaction.svelte";
  import { getUser, permitted } from "~/utils/permissions";
  import type { Transaction as TransactionModel } from "~/integration/junction-hub-api/schemas/transaction";
  import { onMount } from "svelte";
  import integrationInstancesClient from "~/integration-instances-client";
  import type { MaybePromise } from "@sveltejs/kit";
  import Refund from "./refund.svelte";

  export let booking: TripBooking;

  const user = getUser();

  let transactionTask: MaybePromise<TransactionModel | undefined> | undefined;

  onMount(() => {
    if (booking.transactionId) {
      transactionTask = integrationInstancesClient.hub.transactions.get({
        id: booking.transactionId,
      });
    }
  });
</script>

<div class="admin">
  <Transaction {booking} {transactionTask} />

  {#if booking.refund}
    {#if booking.refund.status === "succeeded" || booking.refund.status === "submitted"}
      {#if permitted($user, "refund.view")}
        <Refund refund={booking.refund} />
      {/if}
    {:else if permitted($user, "refund.add")}
      {#await transactionTask then transaction}
        {#if transaction}
          <RefundDialog bind:booking {transaction} />
        {/if}
      {/await}
    {/if}
  {/if}
</div>

<style>
  .admin {
    display: flex;
    flex-flow: column;
    gap: 24px;
  }
</style>
