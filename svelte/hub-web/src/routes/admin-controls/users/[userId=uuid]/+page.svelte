<script lang="ts">
  import UserComponent from "$lib/components/pages/admin-controls/user/user.svelte";
  import type { User } from "~/integration/junction-hub-api/schemas";

  const MOCK_USER: User = {
    id: "mock-id",
    email: "user@example.com",
    role: "reseller-user",
    resellerId: "mock-reseller",
  };
</script>

<UserComponent mode={"update"} user={MOCK_USER} />
