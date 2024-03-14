<script lang="ts" context="module">
  export const LIST_RESELLERS_LIMIT = 20;
</script>

<script lang="ts">
  import { page } from "$app/stores";
  import UserComponent from "$lib/components/pages/admin-controls/user/user.svelte";
  import routeConfig from "$lib/route-config";
  import type { BreadCrumb } from "$lib/models/ui";
  import { getTranslator } from "$lib/i18n";
  import type { User } from "~/integration/junction-hub-api/schemas";

  export let data;

  const t = getTranslator();
  const MOCK_USER: User = {
    id: "mock-id",
    email: "user@example.com",
    role: "reseller-user",
    resellerId: "mock-reseller",
  };

  let breadCrumbs: BreadCrumb[];

  function getUserId(): string {
    const paths = $page.url.pathname.split("/").filter(Boolean);
    const userId = paths[paths.length - 1];

    return userId === undefined ? "" : userId;
  }

  $: resellers = data.resellers;
  $: i18nUsers = $t("pages.adminControls.pages.users", { returnObjects: true });
  $: usersRoute = routeConfig.routes.adminControls.routes.users;
  $: breadCrumbs = [
    { label: i18nUsers.title, url: usersRoute.root },
    { label: MOCK_USER.email, url: usersRoute.routes.update.user(getUserId()).root },
  ];
</script>

<UserComponent mode={"update"} user={MOCK_USER} {breadCrumbs} {resellers} />
