<script lang="ts">
  import { getHexColor, getInitials } from "utils/common";

  export let name: string | undefined = undefined;
  export let imageUrl: string | undefined = undefined;

  $: color = name ? getHexColor(name) : "var(--color-generic-black)";
</script>

{#if imageUrl}
  <img src={imageUrl} alt="" title={name} class="entity-avatar" />
{:else}
  <span class="entity-avatar" style:background-color={color}>
    {name ? getInitials(name) : "?"}
  </span>
{/if}

<style>
  .entity-avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    object-fit: cover;
    object-position: center;
    color: var(--color-generic-white);
    font-weight: 600;
    font-size: 14px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 1;
    letter-spacing: 0.1px;
    border-radius: 50%;
    box-shadow: 0 4px 20px rgb(0 0 0 / 0.05);
    user-select: none;
  }
</style>
