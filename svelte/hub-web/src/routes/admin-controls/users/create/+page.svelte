<script lang="ts">
  import UserComponent from "$lib/components/pages/admin-controls/user/user.svelte";
  import type { UserCreate } from "~/integration/junction-hub-api/schemas";

  const newUser: UserCreate = {
    email: "",
    role: "reseller-user",
    resellerId: "",
  };
</script>

<UserComponent mode={"create"} user={newUser} />
