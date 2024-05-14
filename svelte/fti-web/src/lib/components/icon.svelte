<script context="module" lang="ts">
  export function toAriaLabel(icon: IconTypes | AmenityIcons): string {
    return toTitleCase(icon).replaceAll("-", " ").concat(" icon");
  }
</script>

<script lang="ts">
  import { toTitleCase } from "$lib/helpers/common";
  import type { IconTypes, AmenityIcons } from "$lib/models/common";

  export let variant: IconTypes | AmenityIcons;
  export let size: string | undefined = undefined;
  export let color: string | undefined = undefined;

  const ariaLabel = toAriaLabel(variant);

  $: mask = `url("/icons/${variant}.svg")`;
</script>

<div
  class="icon"
  role="img"
  aria-label={ariaLabel}
  style:mask-image={mask}
  style:-webkit-mask-image={mask}
  style:--size={size}
  style:background-color={color}
/>

<style>
  .icon {
    --x-size: var(--size, 24px);

    display: inline-block;
    width: var(--x-size);
    height: var(--x-size);
    background-color: var(--color-common-light-strong);
    mask-size: contain;
    mask-repeat: no-repeat;
    mask-position: center;
    /* stylelint-disable property-no-vendor-prefix */
    -webkit-mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    -webkit-mask-position: center;
    /* stylelint-enable property-no-vendor-prefix */
  }
</style>
