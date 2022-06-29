<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import AccountIcon from "$lib/icons/account-icon.svelte";
  import NotificationIcon from "$lib/icons/notification-icon.svelte";
  import DashboardSelect from "./dashboard-select.svelte";

  let dashboard: DashboardSelect["$$prop_def"]["value"] = "pay";
</script>

<header>
  <slot />

  <div class="menu">
    <DashboardSelect bind:value={dashboard} />

    <Button variant="empty" class="notification">
      <NotificationIcon />
    </Button>

    <Button variant="empty">
      <AccountIcon />
    </Button>
  </div>
</header>

<style>
  header {
    align-items: center;
    display: flex;
    height: 113px;
    justify-content: space-between;
    padding: 0 49px;
  }

  .menu {
    align-items: center;
    display: flex;
    gap: 26px;
  }

  .menu > :global(button > svg) {
    vertical-align: top;
  }

  .menu > :global(.notification > svg) {
    fill: var(--color-gray-light);
  }
</style>
