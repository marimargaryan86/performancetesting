<script lang="ts">
  import Backdrop from "components/ui/backdrop.svelte";
  import Ticket from "../../../components/ticket.svelte";
  import type { BookingModel } from "integration/junction-mobile-api/schemas/booking";
  import Passengers from "../../../components/passengers.svelte";
  import type { OrderPassengerModel } from "integration/junction-mobile-api/schemas/order";
  import Itinerary from "../../../components/itinerary.svelte";
  import Button from "components/ui/button.svelte";
  import PhoneIcon from "components/icons/phone-icon.svelte";
  import EmailIcon from "components/icons/email-icon.svelte";
  import { pendableCall } from "utils/pendable-call";
  import { callAction } from "utils/common";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { scale } from "svelte/transition";
  import routeConfig from "routeConfig";
  import type { CancelBookingsActionData } from "./+page.server";
  import { createEventDispatcher } from "svelte";

  export let orderId: string;
  export let passengers: OrderPassengerModel[];

  const dispatch = createEventDispatcher<{ success: void }>();

  let backdrop: Backdrop | undefined;
  let booking: BookingModel | undefined = undefined;
  let state: "info" | "confirm" | "done" | "failed";

  $: reservationNo = booking?.operatorBookingReferences.length
    ? booking.operatorBookingReferences.join(", ")
    : undefined;

  const { pending, func: performCancel } = pendableCall(async () => {
    if (!booking) {
      return false;
    }

    const actionData: CancelBookingsActionData = {
      bookingIds: [booking.id],
    };

    const result = await callAction({
      action:
        routeConfig.routes.tripManagement.routes.orders.routes.order(orderId).actions
          .cancelBookings,
      data: actionData,
      dataType: "json",
    });

    if (result.type === "success") {
      return true;
    }

    return false;
  });

  function cancelBooking(): void {
    state = "confirm";
  }

  async function confirm(): Promise<void> {
    const result = await performCancel();
    state = result ? "done" : "failed";

    if (result && booking) {
      booking.cancellationStatus = "pending";

      dispatch("success");
    }
  }

  export function open(nextBooking: BookingModel): void {
    booking = nextBooking;
    state = "info";
    backdrop?.open();
  }

  export function close(): void {
    backdrop?.close();
    booking = undefined;
  }
</script>

<Backdrop bind:this={backdrop}>
  <div
    class="dialog"
    class:wide={state === "info"}
    class:narrow={state !== "info"}
    in:scale={{ duration: 150, start: 0.7, delay: 100 }}
    out:scale={{ duration: 150, start: 0.7 }}
  >
    {#if state === "info"}
      <div class="header">
        <em class="typography body-small">Cancellation</em>
        <h3 class="typography headline-small bold">You are cancelling this booking</h3>
        <Ticket identifier={reservationNo} title="Reservation number" />
      </div>

      <Passengers {passengers} />

      {#if booking}
        <Itinerary bookings={[booking]} />
      {/if}

      <div class="actions">
        <Button variant="outline" on:click={close}>Return to bookings</Button>
        <Button on:click={cancelBooking}>Cancel booking</Button>
      </div>
    {:else if state === "confirm"}
      {#if $pending}
        <div class="pending">
          <LoadingIcon />
        </div>
      {:else}
        <h3 class="typography display-small bold">Are you sure?</h3>
        <p class="typography body-medium">This cannot be undone.</p>

        <div class="actions">
          <Button variant="outline" on:click={close}>No</Button>
          <Button on:click={confirm}>Yes</Button>
        </div>
      {/if}
    {:else if state === "done" || state === "failed"}
      <h3 class="typography display-small bold">
        Cancellation request

        {#if state === "done"}received{:else}failed{/if}
      </h3>

      <div class="typography body-medium info">
        {#if state === "done"}
          <p>
            We have received your cancellation request. A member of our support team will contact
            you shortly with further details.
          </p>
        {/if}

        <p>You can contact Snowfall support on:</p>
      </div>

      <div class="support typography body-medium">
        <strong>
          <PhoneIcon />
          0208 203 2034
        </strong>
        <strong>
          <EmailIcon />
          <a href="mailto:support@snowfalltravel.com">support@snowfalltravel.com</a>
        </strong>
      </div>

      <div class="actions">
        <Button on:click={close}>Return to bookings</Button>
      </div>
    {/if}
  </div>
</Backdrop>

<style>
  .dialog {
    display: flex;
    flex-flow: column;
    gap: 32px;
    width: 100%;
    max-height: calc(100vh - 32px);
    padding: 48px;
    overflow: auto;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .dialog.wide {
    gap: 48px;
    max-width: 642px;
  }

  .dialog.narrow {
    max-width: 482px;
  }

  .header > h3 {
    margin-bottom: 26px;
  }

  .dialog > h3 {
    text-align: center;
  }

  .actions {
    position: sticky;
    bottom: -48px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    margin: -16px -48px -48px;
    padding: 16px 48px 48px;
    background-color: var(--color-common-background-light-main);
  }

  .info {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  p {
    color: var(--color-main-neutral-700);
  }

  .pending {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .support {
    display: flex;
    flex-flow: column;
    gap: 8px;
    align-items: center;
  }

  .support > strong {
    display: flex;
    gap: 8px;
  }

  a {
    color: var(--color-main-primary-500);
    text-decoration: none;
  }
</style>
