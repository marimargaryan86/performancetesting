<script lang="ts">
  import { goto } from "$app/navigation";
  import Table from "$lib/components/ui/table.svelte";
  import ContactIcon from "$lib/icons/contact-icon.svelte";
  import OrderItemsIcon from "$lib/icons/order-items-icon.svelte";
  import OverviewIcon from "$lib/icons/overview-icon.svelte";
  import PersonIcon from "$lib/icons/person-icon.svelte";
  import type { OrderDetailedModel, OrderItemModel } from "$lib/models/order";
  import routeConfig from "$lib/route-config";
  import utils from "$lib/utils";

  export let order: OrderDetailedModel;

  function viewDetails(orderItem: OrderItemModel): void {
    goto(routeConfig.orders.item(order.id, orderItem.id));
  }
</script>

<div class="order">
  <section class="overview">
    <h2><OverviewIcon /> <span>Overview</span></h2>

    <Table>
      <tr slot="head">
        <td>ID</td>
        <td>SPNR</td>
        <td>Reseller</td>
        <td>Price</td>
        <td>Created</td>
        <td>Modified</td>
        <td>Status</td>
      </tr>

      <tr slot="body">
        <td>{order.id.substring(0, 8)}...</td>
        <td>{order.spnr}</td>
        <td>{order.reseller.name}</td>
        <td>{order.price.currency} {order.price.total}</td>
        <td>{order.createdAt.toLocaleDateString(...utils.fullDate)}</td>
        <td>{order.modifiedAt.toLocaleDateString(...utils.fullDate)}</td>
        <td>{order.status}</td>
      </tr>
    </Table>
  </section>

  <section class="contact-details">
    <h2><ContactIcon /> <span>Contact details</span></h2>

    <Table>
      <tr slot="head">
        <td>E-mail</td>
        <td>Phone</td>
        <td>Address</td>
      </tr>

      <tr slot="body">
        <td>
          <a href="mailto:{order.contactDetails.email}" title="Send E-mail">
            {order.contactDetails.email}
          </a>
        </td>
        <td>{order.contactDetails.phone}</td>
        <td>{order.contactDetails.address}</td>
      </tr>
    </Table>
  </section>

  <section class="passengers">
    <h2><PersonIcon /> <span>Passengers</span></h2>

    <Table>
      <tr slot="head">
        <td>Name title</td>
        <td>First name</td>
        <td>Last name</td>
        <td>Gender</td>
        <td>Date of birth</td>
      </tr>

      <svelte:fragment slot="body">
        {#each order.passengers as passenger}
          <tr>
            <td>{passenger.title}</td>
            <td>{passenger.firstName}</td>
            <td>{passenger.lastName}</td>
            <td>{passenger.gender}</td>
            <td>{passenger.dateOfBirth.toLocaleDateString(...utils.fullDate)}</td>
          </tr>
        {/each}
      </svelte:fragment>
    </Table>
  </section>

  <section class="order-items">
    <h2><OrderItemsIcon /> <span>Order items</span></h2>

    <Table>
      <tr slot="head">
        <td>ID</td>
        <td>Type</td>
        <td>Provider</td>
        <td>Trips</td>
        <td>Price</td>
        <td>Status</td>
      </tr>

      <svelte:fragment slot="body">
        {#each order.items as item}
          <tr
            on:click={() => viewDetails(item)}
            style:cursor="pointer"
            title="Click to view details"
          >
            <td>{item.id.substring(0, 8)}...</td>
            <td>{item.type}</td>
            <td>{item.provider.name}</td>
            <td>{item.trips.length}</td>
            <td>{item.price.currency} {item.price.total}</td>
            <td>{item.status}</td>
          </tr>
        {/each}
      </svelte:fragment>
    </Table>
  </section>
</div>

<style>
  .order {
    padding: 8px;
  }

  section {
    box-shadow: var(--drop-shadow-light);
  }

  section > :global(.table) {
    width: 100%;
  }

  section:not(:last-child) {
    margin-bottom: 16px;
  }

  h2 {
    user-select: none;
    padding: 8px;
    background-color: var(--color-teal);
  }

  h2 > :global(*) {
    vertical-align: middle;
    color: var(--color-white);
    font-size: 16px;
  }

  .passengers > h2 > :global(*),
  .overview > h2 > :global(*),
  .contact-details > h2 > :global(*) {
    fill: var(--color-white);
  }

  .order-items > h2 > :global(*) {
    stroke: var(--color-white);
  }
</style>
