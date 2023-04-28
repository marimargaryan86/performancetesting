<script lang="ts" context="module">
  function parseBooking(data: BookingModel): BookingModel {
    return {
      ...data,
      details: data.details
        ? {
            ...data.details,
            legs: data.details.legs.map((item) => ({
              ...item,
              arrivalAt: new Date(item.arrivalAt),
              departureAt: new Date(item.departureAt),
            })),
          }
        : undefined,
      order: data.order
        ? {
            ...data.order,
            passengers: data.order.passengers.map((item) => ({
              ...item,
              dateOfBirth: new Date(item.dateOfBirth),
            })),
          }
        : undefined,
    };
  }
</script>

<script lang="ts">
  import { portal } from "directives/portal";
  import type { TransactionModel } from "models/transaction";
  import { fade, fly } from "svelte/transition";
  import Summary from "./summary.svelte";
  import Billing from "./billing.svelte";
  import Journey from "./journey/journey.svelte";
  import Passengers from "./passengers.svelte";
  import Button from "components/ui/button.svelte";
  import type { BookingModel } from "models/booking";
  import LoadingIcon from "components/icons/loading-icon.svelte";

  export let transaction: TransactionModel | undefined;

  let bookingRequest: Promise<BookingModel | undefined> | undefined;

  $: updateBooking(transaction);

  function updateBooking(nextTransaction?: TransactionModel): void {
    if (!nextTransaction) {
      bookingRequest = undefined;

      return;
    }

    bookingRequest = fetch(`/api/bookings/${nextTransaction.bookingId}`).then((resp) => {
      if (resp.status !== 200) {
        return undefined;
      }

      return resp.json().then((data) => parseBooking(data));
    });
  }

  function close(): void {
    transaction = undefined;
  }
</script>

{#if transaction}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div
    class="transaction-details"
    on:click|self={close}
    use:portal={document.body}
    transition:fade|local={{ duration: 200 }}
  >
    <div class="dialogue" transition:fly|local={{ duration: 200, y: 24 }}>
      {#await bookingRequest}
        <div class="pending">
          <span class="typography headline-small">Fetching booking</span>
          <LoadingIcon />
        </div>
      {:then booking}
        {#if booking}
          <div class="header">
            <h1>
              <strong class="typography headline-small bold">ID:</strong>
              <span class="typography body-xlarge">{booking.id}</span>
            </h1>

            <h2 class="typography body-small">
              Updated: {transaction.createdAt.toLocaleDateString("en-GB", {
                hour: "2-digit",
                minute: "2-digit",
                year: "2-digit",
                month: "2-digit",
                day: "2-digit",
              })}
            </h2>
          </div>

          <div class="content">
            <div class="row">
              <Summary {booking} {transaction} />
              <Billing {booking} />
            </div>

            <div class="row">
              <Journey {booking} />
              <Passengers passengers={booking.order?.passengers ?? []} />
            </div>
          </div>

          <div class="actions">
            <Button on:click={close} size="medium">Return</Button>
          </div>
        {:else}
          <div class="not-found typography headline-small">Booking not found</div>
        {/if}
      {/await}
    </div>
  </div>
{/if}

<style>
  .transaction-details {
    position: fixed;
    top: 0;
    left: 0;
    z-index: var(--z-index-overlay);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    background-color: rgb(0 0 0 / 0.5);
  }

  .dialogue {
    display: flex;
    flex-flow: column;
    gap: 32px;
    width: 100%;
    max-width: 960px;
    margin: 16px;
    padding: 24px 48px;
    color: var(--color-main-neutral-800);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgb(0 0 0 / 0.1);
  }

  .pending,
  .not-found {
    display: flex;
    gap: 8px;
    align-items: center;
    align-self: center;
  }

  h1 {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 4px;
    color: var(--color-main-neutral-800);
  }

  h2 {
    color: var(--color-main-neutral-700);
  }

  .content {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .content > .row {
    display: flex;
    gap: 16px;
  }

  .content > .row > :global(*) {
    flex-grow: 1;
  }

  .actions {
    display: flex;
    gap: 16px;
    justify-content: flex-end;
  }
</style>
