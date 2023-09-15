<script lang="ts">
  import TicketIcon from "components/icons/ticket-icon.svelte";
  import Passengers from "../../../components/passengers.svelte";

  export let data;
</script>

<svelte:head>
  <title>
    Details · {data.order.journey?.reference ?? "Unknown"} · Orders · Trip Management · Junction Hub
  </title>
</svelte:head>

<div class="content">
  <h3 class="typography title-large bold">Order details</h3>

  <div class="ticket">
    <div class="icon">
      <TicketIcon color="var(--color-main-primary-600)" />
    </div>

    <span>
      <em class="typography body-xsmall">Order reference</em>
      <strong class="typography body-medium bold">
        {data.order.journey?.reference ?? "Unknown"}
      </strong>
    </span>
  </div>

  <Passengers passengers={data.order.passengers} />
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    gap: 24px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  h3 {
    color: var(--color-main-neutral-800);
  }

  .ticket {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: var(--color-main-primary-500) 1px solid;
    border-radius: 50%;
  }

  .ticket > span {
    display: flex;
    flex-flow: column;
  }

  .ticket em {
    color: var(--color-main-primary-700);
  }

  .content > :global(.passengers) {
    margin-top: 24px;
  }
</style>
