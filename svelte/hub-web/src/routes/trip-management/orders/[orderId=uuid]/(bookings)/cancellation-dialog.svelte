<script lang="ts">
  import Backdrop from "components/ui/backdrop.svelte";
  import Ticket from "../../../components/ticket.svelte";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import Passengers from "../../../components/passengers.svelte";
  import type { OrderPassenger } from "integration/junction-hub-api/schemas/order";
  import Itinerary from "../../../components/itinerary.svelte";
  import Button from "components/ui/button.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { scale } from "svelte/transition";
  import { createEventDispatcher } from "svelte";
  import integrationInstancesClient from "integration-instances-client";
  import { writable } from "svelte/store";
  import type { CancellationRequest } from "integration/junction-hub-api/schemas/cancellation";
  import { getLocaleData } from "i18n";
  import Icon from "components/icons/icon.svelte";

  export let passengers: OrderPassenger[];

  const i18n = getLocaleData();
  const dispatch = createEventDispatcher<{ success: void }>();

  let backdrop: Backdrop | undefined;
  let booking: TripBooking | undefined = undefined;
  let state: "info" | "rules" | "confirm" | "done" | "failed";

  const pending = writable(false);

  $: reservationNo = booking?.operatorBookingReferences.length
    ? booking.operatorBookingReferences.join(", ")
    : undefined;

  async function performCancel(): Promise<CancellationRequest | undefined> {
    if ($pending) {
      return;
    }

    try {
      $pending = true;

      if (!booking) {
        return undefined;
      }

      return await integrationInstancesClient.hub.cancellationRequests.create({
        data: { bookingIds: [booking.id] },
      });
    } catch {
      return undefined;
    } finally {
      $pending = false;
    }
  }

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
    if ($pending) {
      return;
    }

    const result = await performCancel();
    state = result ? "done" : "failed";

    if (result && booking) {
      booking.cancellationId = result.id;
      booking.cancellation = {
        bookingId: booking.id,
        id: result.id,
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
        <em typography="body-small">{$i18n.words.cancellation}</em>
        <h3 typography="headline-small" weight="bold">
          {$i18n.sentences.youAreCancellingThisBooking}
        </h3>
        <Ticket identifier={reservationNo} title={$i18n.words.reservationNumber} />
      </div>

      <Passengers {passengers} />

      {#if booking}
        <Itinerary bookings={[booking]} />
      {/if}

      <div class="actions">
        <Button variant="outline" on:click={close}>{$i18n.actions.returnToBookings}</Button>
        <Button on:click={rules}>{$i18n.actions.cancelBooking}</Button>
      </div>
    {:else if state === "rules" && booking?.rules}
      <div class="icon-wrapper">
        <Icon color="var(--color-semantic-error-500)" size="64px" variant="alert-disc" />
      </div>

      <h3 typography="display-small" weight="bold">{$i18n.sentences.rulesAndFees}</h3>

      <p typography="title-small">
        {$i18n.sentences.pleaseReviewTheFollowingRules}
      </p>

      {#each booking.rules as rule}
        <h3 typography="headline-medium">{rule.title}</h3>

        <p typography="body-small">{rule.body}</p>
      {/each}

      <p typography="body-medium">{$i18n.sentences.doYouWishToContinue}</p>

      <div class="actions">
        <Button variant="outline" on:click={info}>{$i18n.actions.goBack}</Button>
        <Button on:click={cancelBooking}>{$i18n.actions.continue}</Button>
      </div>
    {:else if state === "confirm"}
      {#if $pending}
        <div class="pending">
          <LoadingIcon />
        </div>
      {:else}
        <h3 typography="display-small" weight="bold">{$i18n.sentences.areYouSure}</h3>
        <p typography="body-medium">{$i18n.sentences.thisCannotBeUndone}</p>

        <div class="actions">
          <Button variant="outline" on:click={close}>{$i18n.words.no}</Button>
          <Button on:click={confirm}>{$i18n.words.yes}</Button>
        </div>
      {/if}
    {:else if state === "done" || state === "failed"}
      <h3 typography="display-small" weight="bold">
        {#if state === "done"}
          {$i18n.sentences.cancellationRequestReceived}
        {:else}
          {$i18n.sentences.cancellationRequestFailed}
        {/if}
      </h3>

      <div typography="body-medium" class="info">
        {#if state === "done"}
          <p>
            {$i18n.sentences.cancellationRequestInfo}
          </p>
        {/if}

        <p>{$i18n.sentences.contactSnowfallSupport}:</p>
      </div>

      <div class="support" typography="body-medium">
        <strong>
          <Icon variant="email" size="20px" />
          <a href="mailto:support@snowfalltravel.com?subject=GG%20-%20">
            support@snowfalltravel.com
          </a>
        </strong>
      </div>

      <div class="actions">
        <Button on:click={close}>{$i18n.actions.returnToBookings}</Button>
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
