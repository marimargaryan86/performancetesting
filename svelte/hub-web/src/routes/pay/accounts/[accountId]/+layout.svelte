<script lang="ts">
  import type { LayoutData } from "./$types";
  import BreadCrumbs from "components/page/bread-crumbs.svelte";

  export let data: LayoutData;

  $: breadCrumbs = [
    { url: "/pay/accounts", label: "Accounts" },
    { url: `/pay/accounts/${data.account.id}`, label: data.account.name },
  ];
</script>

<BreadCrumbs items={breadCrumbs} />

<slot />
