<script lang="ts">
  import { getHexColor, getInitials } from "utils/common";

  export let name: string | undefined = undefined;
  export let imageUrl: string | undefined = undefined;
  export let size = "34px";

  $: color = name ? getHexColor(name) : "var(--color-generic-black)";
</script>

{#if imageUrl}
  <img src={imageUrl} alt="" title={name} class="entity-avatar" style:--size={size} />
{:else}
  <span
    class="entity-avatar typography body-small bold"
    style:background-color={color}
    style:--size={size}
  >
    {name ? getInitials(name) : "?"}
  </span>
{/if}

<style>
  span.entity-avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: var(--size);
    height: var(--size);
    object-fit: cover;
    object-position: center;
    color: var(--color-generic-white);
    font-size: calc(var(--size) * 0.4);
    text-shadow: 0 0 1px rgb(0 0 0 / 1), 0 0 2px rgb(0 0 0 / 1);
    border-radius: 50%;
    box-shadow: 0 4px 20px rgb(0 0 0 / 0.05);
    user-select: none;
  }
</style>
