<script lang="ts" context="module">
  import type { Direction } from "models/spatial";

  const directionMapping: Record<Direction, number> = {
    right: 0,
    down: 90,
    left: 180,
    up: 270,
  };
</script>

<script lang="ts">
  export let color = "var(--color-generic-black)";
  export let direction: Direction = "right";
</script>

<svg
  width="16"
  height="16"
  viewBox="0 0 16 16"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  style:--rotation="{directionMapping[direction]}deg"
  class="chevron-icon"
>
  <path
    d="M5.59998 4L9.59998 8L5.59998 12"
    stroke={color}
    stroke-width="1.67"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
</svg>

<style>
  .chevron-icon {
    transform: rotateZ(var(--rotation));
    transition: transform 150ms ease;
  }
</style>
