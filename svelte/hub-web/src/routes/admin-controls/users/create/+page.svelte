<script lang="ts" context="module">
  export const LIST_RESELLERS_LIMIT = 20;
</script>

<script lang="ts">
  import UserComponent from "$lib/components/pages/admin-controls/user/user.svelte";
  import type { UserPut } from "~/integration/junction-hub-api/schemas";
  import routeConfig from "$lib/route-config";
  import type { BreadCrumb } from "$lib/models/ui";
  import { getTranslator } from "$lib/i18n";

  const t = getTranslator();
  let breadCrumbs: BreadCrumb[];

  $: i18nUsers = $t("pages.adminControls.pages.users", { returnObjects: true });
  $: usersRoute = routeConfig.routes.adminControls.routes.users;
  $: breadCrumbs = [
    { label: i18nUsers.title, url: usersRoute.root },
    { label: i18nUsers.pages.create.title, url: usersRoute.routes.create.root },
  ];

  const newUser: UserPut = {
    email: "",
    role: "reseller-user",
    resellerId: "",
  };
</script>

<UserComponent mode={"create"} user={newUser} {breadCrumbs} />
