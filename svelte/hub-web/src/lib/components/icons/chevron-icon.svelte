<script lang="ts" context="module">
  const directionMapping: Record<Direction, number> = {
    right: 0,
    down: 90,
    left: 180,
    up: 270,
  };
</script>

<script lang="ts">
  import type { Direction } from "$lib/models/spatial";

  export let color = "var(--color-common-light-strong)";
  export let direction: Direction = "right";
  export let size = "16px";
  export let variant: "outlined" | "filled" = "outlined";
</script>

<svg
  style:--size={size}
  viewBox="0 0 16 16"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  style:--rotation="{directionMapping[direction]}deg"
  class="chevron-icon"
>
  {#if variant === "filled"}
    <path
      d="M11.0567 8.9194L6.63636 4.6329C6.36054 4.3655 5.83325 4.5276 5.83325 4.8799L5.83325 13.4528C5.83325 13.8051 6.36054 13.9672 6.63636 13.6997L11.0567 9.41328C11.2032 9.27118 11.2032 9.0615 11.0567 8.9194Z"
      fill={color}
    />
  {:else}
    <path
      d="M5.59998 4L9.59998 8L5.59998 12"
      stroke={color}
      stroke-width="1.67"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  {/if}
</svg>

<style>
  .chevron-icon {
    width: var(--size);
    height: var(--size);
    transform: rotateZ(var(--rotation));
    transition: transform 150ms ease;
  }
</style>
