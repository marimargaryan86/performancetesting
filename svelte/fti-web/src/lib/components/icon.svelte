<script lang="ts">
  import type { IconTypes } from "$lib/models/common";

  export let variant: IconTypes;
  export let size: string | undefined = undefined;
  export let color: string | undefined = undefined;

  $: mask = `url("/icons/${variant}.svg")`;
</script>

<div
  class="icon"
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
