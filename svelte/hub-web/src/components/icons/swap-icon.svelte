<script lang="ts">
  export let color: string = "var(--color-main-primary-500)";
  export let size: number = 23;
  export let rotate = false;
  export let standard = true;

  const width = Math.round(size * (27 / 23) + Number.EPSILON);
</script>

<div class:rotate class:standard style:width={`${width}px`} style:height={`${size}px`}>
  <svg xmlns="http://www.w3.org/2000/svg" {width} height={size} fill="none"
    ><path
      fill={color}
      fill-rule="evenodd"
      d="M18.9.78a.836.836 0 0 1 1.18 0l6.676 6.656a.83.83 0 0 1 0 1.176l-6.675 6.656a.836.836 0 0 1-1.18 0 .83.83 0 0 1 0-1.176l5.25-5.236H12.26a.833.833 0 1 1 0-1.664h11.892l-5.25-5.236a.83.83 0 0 1 0-1.176M8.1 22.756a.836.836 0 0 1-1.18 0L.243 16.1a.83.83 0 0 1 0-1.176L6.92 8.268a.836.836 0 0 1 1.18 0 .83.83 0 0 1 0 1.176L2.85 14.68H14.74a.833.833 0 1 1 0 1.664H2.849l5.25 5.236a.83.83 0 0 1 0 1.176"
      clip-rule="evenodd"
    /></svg
  >
</div>

<style>
  .rotate {
    transform: rotate(180deg);
    transition: transform 0.3s ease;
  }

  .standard {
    transform: rotate(-180deg);
    transition: transform 0.3s ease;
  }
</style>
