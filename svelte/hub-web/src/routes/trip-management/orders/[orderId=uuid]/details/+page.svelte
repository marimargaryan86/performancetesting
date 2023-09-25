<script lang="ts">
  import Passengers from "../../../components/passengers.svelte";
  import Ticket from "../../../components/ticket.svelte";

  export let data;
</script>

<svelte:head>
  <title>
    Details · {data.order.journey?.reference ?? "Unknown"} · Orders · Trip Management · Junction Hub
  </title>
</svelte:head>

<div class="content">
  <h3 class="typography title-large bold">Order details</h3>

  <Ticket identifier={data.order.journey?.reference} />

  <Passengers passengers={data.order.passengers} />
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    gap: 24px;
    max-width: 1152px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  h3 {
    color: var(--color-main-neutral-800);
  }

  .content > :global(.passengers) {
    margin-top: 24px;
  }
</style>
