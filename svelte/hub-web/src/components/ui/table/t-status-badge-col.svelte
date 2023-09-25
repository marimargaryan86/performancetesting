<script lang="ts">
  import StatusBadge, { type StatusBadgeValue } from "../status-badge.svelte";
  import TCol from "./t-col.svelte";

  export let value: StatusBadgeValue;
</script>

<TCol class="status-badge-col" width="0">
  <StatusBadge {value} />
</TCol>

<style>
  :global(.status-badge-col > div > .status-badge) {
    width: 100%;
  }
</style>
