<script lang="ts">
  import { page } from "$app/stores";

  export let href: string;
  export let exact = false;
  let className: string | undefined = undefined;
  export { className as class };
  export let activeClass = "active";

  $: exactActive = $page.url.pathname === href;
  $: partialActive = $page.url.pathname.startsWith(href);
  $: active = (exact && exactActive) || (!exact && partialActive);
</script>

<a {href} class="{className ?? ''} {active ? activeClass : ''}">
  <slot />
</a>
