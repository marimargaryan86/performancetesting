<script lang="ts">
  import RefundDialog from "$lib/components/pages/trip-management/orders/refund-dialog.svelte";
  import Transaction from "$lib/components/pages/trip-management/orders/transaction.svelte";
  import { getUser, permitted } from "$lib/utils/permissions";
  import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
  import { onMount } from "svelte";
  import integrationInstancesClient from "~/integration-instances-client";
  import type { MaybePromise } from "@sveltejs/kit";
  import Refund from "$lib/components/pages/trip-management/orders/refund.svelte";

  export let booking: HubSchemas.TripBooking;

  const user = getUser();

  let transactionTask: MaybePromise<HubSchemas.Transaction | undefined> | undefined;

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
