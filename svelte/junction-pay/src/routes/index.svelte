<script lang="ts">
  import { goto } from "$app/navigation";
  import routeConfig from "$lib/route-config";
  import { onMount } from "svelte";

  onMount(() => goto(routeConfig.login));
</script>
