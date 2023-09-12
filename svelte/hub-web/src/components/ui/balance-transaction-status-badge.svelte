<script lang="ts">
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";
  import { capitalize } from "utils/common";

  export let value: "completed" | "pending" | "deleted";

  const variants: Record<"completed" | "pending" | "deleted", StatusBadgeVariant> = {
    completed: "ok",
    pending: "warn",
    deleted: "error",
  };

  $: variant = variants[value];
</script>

<StatusBadge {variant} value={capitalize(value)} />
