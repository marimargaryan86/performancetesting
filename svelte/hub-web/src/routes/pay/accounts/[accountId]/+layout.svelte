<script lang="ts">
  import BreadCrumbs from "components/page/bread-crumbs.svelte";
  import routeConfig from "routeConfig";

  export let data;

  $: breadCrumbs = [
    { url: routeConfig.pay.accounts.root, label: "Accounts" },
    { url: routeConfig.pay.accounts.account(data.account.id), label: data.account.name },
  ];
</script>

<BreadCrumbs items={breadCrumbs} />

<slot />
