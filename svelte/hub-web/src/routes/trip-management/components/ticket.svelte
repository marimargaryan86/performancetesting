<script lang="ts">
  import TicketIcon from "components/icons/ticket-icon.svelte";

  export let reference: string | undefined = undefined;
</script>

<div class="ticket">
  <div class="icon">
    <TicketIcon color="var(--color-main-primary-600)" />
  </div>

  <span>
    <em class="typography body-xsmall">Order reference</em>
    <strong class="typography body-medium bold">
      {reference ?? "Unknown"}
    </strong>
  </span>
</div>

<style>
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
</style>
