<script lang="ts" context="module">
  export const LIST_RESELLERS_LIMIT = 20;
</script>

<script lang="ts">
  import UserComponent from "$lib/components/pages/admin-controls/user/user.svelte";
  import type { UserCreate } from "~/integration/junction-hub-api/schemas";

  export let data;

  const newUser: UserCreate = {
    email: "",
    role: "reseller-user",
    resellerId: "",
  };

  $: resellers = data.resellers;
</script>

<UserComponent mode={"create"} user={newUser} {resellers} />
