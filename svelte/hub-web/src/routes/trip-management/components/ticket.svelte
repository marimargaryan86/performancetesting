<script lang="ts">
  import TicketIcon from "components/icons/ticket-icon.svelte";
  import { getLocaleData } from "i18n";

  let titleExt: string | undefined = undefined;
  export { titleExt as title };
  export let identifier: string | undefined = undefined;

  const i18n = getLocaleData();

  $: title = titleExt ?? $i18n.words.orderReference;
</script>

<div class="ticket">
  <div class="icon">
    <TicketIcon color="var(--color-main-primary-600)" />
  </div>

  <span>
    <em class="typography body-xsmall">{title}</em>
    <strong class="typography body-medium bold">
      {identifier ?? $i18n.words.notAvailable}
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
