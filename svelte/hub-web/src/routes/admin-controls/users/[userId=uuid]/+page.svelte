<script lang="ts">
  import { page } from "$app/stores";
  import UserComponent from "$lib/components/pages/admin-controls/user/user.svelte";
  import routeConfig from "$lib/route-config";
  import type { BreadCrumb } from "$lib/models/ui";
  import { getTranslator } from "$lib/i18n";

  export let data;

  const t = getTranslator();
  let breadCrumbs: BreadCrumb[];

  function getUserId(): string {
    const paths = $page.url.pathname.split("/").filter(Boolean);
    const userId = paths[paths.length - 1];

    return userId === undefined ? "" : userId;
  }

  $: i18nUsers = $t("pages.adminControls.pages.users", { returnObjects: true });
  $: usersRoute = routeConfig.routes.adminControls.routes.users;
  $: breadCrumbs = [
    { label: i18nUsers.title, url: usersRoute.root },
    { label: data.user.email, url: usersRoute.routes.update.user(getUserId()).root },
  ];
</script>

<UserComponent mode={"update"} user={data.user} {breadCrumbs} />
