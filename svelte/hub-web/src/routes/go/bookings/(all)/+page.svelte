<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import TCompanyCol from "components/ui/table/t-company-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import TransactionStatusBadge from "components/ui/transaction-status-badge.svelte";
  import Alert from "components/ui/alert.svelte";
  import TripletIcon from "components/icons/triplet-icon.svelte";
  import type { FlattenedObject } from "utils/common";
  import type { TransactionModel } from "models/transaction";
  import type { DirectionY } from "models/spatial";
  import { onMount } from "svelte";

  const bookings: string[] = ["a", "b", "c", "d", "e"];

  let sortGroup: FlattenedObject<TransactionModel> = "createdAt";
  let sortDirection: DirectionY = "down";
  let alert = false;

  onMount(() => {
    alert = history.state?.alert;
  });
</script>

<svelte:head>
  <title>All · Bookings · Go · Junction Hub</title>
</svelte:head>

{#if alert}
  <Alert type={alert.type}>{alert.message}</Alert>
{/if}

<div class="content">
  <Table class="bookings-table">
    <THead>
      <Header>Booking Reference</Header>
      <Header>Passenger Name</Header>
      <Header>Ticket</Header>
      <Header bind:sortGroup bind:sortDirection sortValue="departure">Departure Date</Header>
      <Header>Provider</Header>
      <Header>Reseller</Header>
      <Header bind:sortGroup bind:sortDirection sortValue="createdAt">Created Date</Header>
      <Header>Total Price</Header>
      <Header bind:sortGroup bind:sortDirection sortValue="status">Booking Status</Header>
      <Header bind:sortGroup bind:sortDirection sortValue="refund.status">Refund Status</Header>
      <Header />
    </THead>

    <TBody>
      {#each bookings as _}
        <TRow alternatingBackground={false}>
          <TCol maxWidth="96px" copyable class="green">123ABC456</TCol>
          <TCol>Jerry Smith</TCol>
          <TCol class="green">Download</TCol>
          <TCol>02/11/23</TCol>
          <TCompanyCol maxWidth="160px" companyName="Renfe" img="/images/renfe-logo.png" />
          <TCompanyCol maxWidth="160px" companyName="Malaga TA" />
          <TCol>02/11/23</TCol>
          <TMoneyCol money={{ amount: 2952.9, currency: "USD" }} />
          <TCol width="80px">
            <TransactionStatusBadge value="pending" />
          </TCol>
          <TCol maxWidth="96px" class="green">View</TCol>
          <TActionsCol>
            <TripletIcon />
          </TActionsCol>
        </TRow>
      {/each}
    </TBody>
  </Table>
</div>

<style>
  .content > :global(.table.booking-table) {
    width: 100%;
    height: 100%;
    color: var(--color-common-light-strong);
  }

  .content > :global(.table.bookings-table .status-badge) {
    width: 100%;
  }

  .content > :global(.table.bookings-table tbody tr) {
    cursor: pointer;
  }

  .content :global(tr:hover .actions) {
    opacity: 1;
    pointer-events: all;
  }

  .content :global(.green) {
    color: var(--color-main-primary-500);
  }

  .content :global(td:hover .green) {
    color: var(--color-common-dark-strong);
  }
</style>
