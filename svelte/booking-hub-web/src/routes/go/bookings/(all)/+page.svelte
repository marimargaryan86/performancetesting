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

  const bookings: string[] = ["a", "b", "c"];
</script>

<svelte:head>
  <title>All · Bookings · Go · Junction Hub</title>
</svelte:head>

<div class="content">
  <Table class="bookings-table">
    <THead>
      <Header>Booking Reference</Header>
      <Header>Passenger Name</Header>
      <Header>Departure Date</Header>
      <Header>Provider</Header>
      <Header>Reseller</Header>
      <Header>Created Date</Header>
      <Header>Total Price</Header>
      <Header>Provider Status</Header>
      <Header>Pay Transaction</Header>
      <Header />
    </THead>

    <TBody>
      {#each bookings as _}
        <TRow alternatingBackground={false}>
          <TCol maxWidth="96px" copyable>123ABC456</TCol>
          <TCol>Jerry Smith</TCol>
          <TCol>02/11/23</TCol>
          <TCompanyCol maxWidth="160px" companyName="Air France" />
          <TCompanyCol maxWidth="160px" companyName="ABC Travel" />
          <TCol>02/11/23</TCol>
          <TMoneyCol money={{ amount: 2952.9, currency: "USD" }} />
          <TCol width="80px">
            <TransactionStatusBadge value="pending" />
          </TCol>
          <TCol maxWidth="96px">View</TCol>
          <TActionsCol>
            <button class="action outline typography body-medium bold">Cancel</button>
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

  .action.outline {
    padding: 6px 16px;
    color: var(--color-common-light-strong);
    text-decoration: none;
    background-color: var(--color-common-dark-strong);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
    cursor: pointer;
  }

  .content :global(tr:hover .actions) {
    opacity: 1;
    pointer-events: all;
  }
</style>
