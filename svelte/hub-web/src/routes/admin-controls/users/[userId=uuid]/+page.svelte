<script lang="ts" context="module">
  export const LIST_RESELLERS_LIMIT = 20;
</script>

<script lang="ts">
  import UserComponent from "$lib/components/pages/admin-controls/user/user.svelte";
  import type { User } from "~/integration/junction-hub-api/schemas";

  export let data;

  const MOCK_USER: User = {
    id: "mock-id",
    email: "user@example.com",
    role: "reseller-user",
    resellerId: "mock-reseller",
  };

  $: resellers = data.resellers;
</script>

<UserComponent mode={"update"} user={MOCK_USER} {resellers} />
