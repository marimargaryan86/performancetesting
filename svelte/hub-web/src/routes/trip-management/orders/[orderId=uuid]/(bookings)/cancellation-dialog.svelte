<script lang="ts">
  import AlertIcon from "components/icons/alert-icon.svelte";
  import Backdrop from "components/ui/backdrop.svelte";
  import Ticket from "../../../components/ticket.svelte";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import Passengers from "../../../components/passengers.svelte";
  import type { OrderPassenger } from "integration/junction-hub-api/schemas/order";
  import Itinerary from "../../../components/itinerary.svelte";
  import Button from "components/ui/button.svelte";
  import EmailIcon from "components/icons/email-icon.svelte";
  import { pendableCall } from "utils/pendable-call";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { scale } from "svelte/transition";
  import { createEventDispatcher } from "svelte";
  import integrationInstancesClient from "integration-instances-client";

  export let passengers: OrderPassenger[];

  const dispatch = createEventDispatcher<{ success: void }>();

  let backdrop: Backdrop | undefined;
  let booking: TripBooking | undefined = undefined;
  let state: "info" | "rules" | "confirm" | "done" | "failed";

  $: reservationNo = booking?.operatorBookingReferences.length
    ? booking.operatorBookingReferences.join(", ")
    : undefined;

  const { pending, func: performCancel } = pendableCall(async () => {
    if (!booking) {
      return undefined;
    }

    try {
      return await integrationInstancesClient.hub.cancellationRequests.create({
        data: { bookingIds: [booking.id] },
      });
    } catch {
      return undefined;
    }
  });

  function info(): void {
    state = "info";
  }

  function rules(): void {
    state = "rules";
  }

  function cancelBooking(): void {
    state = "confirm";
  }

  async function confirm(): Promise<void> {
    const result = await performCancel();
    state = result ? "done" : "failed";

    if (result && booking) {
      booking.cancellation = {
        bookingId: booking.id,
        id: "",
        status: result.status,
        booking,
      };

      dispatch("success");
    }
  }

  export function open(nextBooking: TripBooking): void {
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
        <Button on:click={rules}>Cancel booking</Button>
      </div>
    {:else if state === "rules" && booking?.rules}
      <div class="icon-wrapper">
        <AlertIcon color="var(--color-semantic-error-500)" size="64px" variant="disc" />
      </div>

      <h3 class="typography display-small bold">Rules and Fees</h3>

      <p class="typography title-small">
        Please review the following rules before cancelling, including any applicable fees.
      </p>

      {#each booking.rules as rule}
        <h3 class="typography display-small">{rule.title}</h3>

        <p class="typography body-small">{rule.body}</p>
      {/each}

      <p class="typography body-medium">Do you wish to continue?</p>

      <div class="actions">
        <Button variant="outline" on:click={info}>Go back</Button>
        <Button on:click={cancelBooking}>Continue</Button>
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
          <EmailIcon />
          <a href="mailto:support@snowfalltravel.com?subject=GG%20-%20"
            >support@snowfalltravel.com</a
          >
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

  .icon-wrapper {
    display: flex;
    justify-content: center;
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
