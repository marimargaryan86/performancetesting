<script lang="ts">
  import { dev } from "$app/environment";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import TCompanyCol from "components/ui/table/t-company-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";

  const bookings: string[] = ["a", "b", "c", "d", "e"];
</script>

<svelte:head>
  <title>All · Bookings · Go · Junction Hub</title>
</svelte:head>

{#if !dev}
  <div />
{:else}
  <Table class="bookings-table">
    <THead>
      <Header>Booking Reference</Header>
      <Header>Passenger Name</Header>
      <Header>Ticket</Header>
      <Header>Departure Date</Header>
      <Header>Provider</Header>
      <Header>Reseller</Header>
      <Header>Created Date</Header>
      <Header>Total Price</Header>
      <Header>Booking Status</Header>
      <Header>Refund Status</Header>
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
          <TStatusBadgeCol value="pending" />
          <TCol maxWidth="96px" class="green">View</TCol>
        </TRow>
      {/each}
    </TBody>
  </Table>
{/if}

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
