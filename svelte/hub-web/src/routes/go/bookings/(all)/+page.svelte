<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import TCompanyCol from "components/ui/table/t-company-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import TransactionStatusBadge from "components/ui/transaction-status-badge.svelte";
  import type { FlattenedObject } from "utils/common";
  import type { TransactionModel } from "models/transaction";
  import type { DirectionY } from "models/spatial";

  const bookings: string[] = ["a", "b", "c", "d", "e"];

  let sortGroup: FlattenedObject<TransactionModel> = "createdAt";
  let sortDirection: DirectionY = "down";
</script>

<svelte:head>
  <title>All · Bookings · Go · Junction Hub</title>
</svelte:head>

<Table class="bookings-table">
  <THead>
    <Header>Booking Reference</Header>
    <Header>Passenger Name</Header>
    <Header>Ticket</Header>
    <Header bind:sortGroup bind:sortDirection>Departure Date</Header>
    <Header>Provider</Header>
    <Header>Reseller</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="createdAt">Created Date</Header>
    <Header>Total Price</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="status">Booking Status</Header>
    <Header bind:sortGroup bind:sortDirection>Refund Status</Header>
  </THead>

  <TBody>
    {#each bookings as booking}
      <TRow alternatingBackground={false}>
        <TCol maxWidth="96px" copyable class="green">123ABC456{booking}</TCol>
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
      </TRow>
    {/each}
  </TBody>
</Table>

<style>
  :global(.table.bookings-table) {
    width: 100%;
    height: 100%;
  }

  :global(.table.bookings-table .status-badge) {
    width: 100%;
  }

  :global(.table.bookings-table tbody tr) {
    cursor: pointer;
  }

  :global(.green) {
    color: var(--color-main-primary-500);
  }
</style>
