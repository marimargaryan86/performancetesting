<script lang="ts">
  export let color = "var(--color-common-light-strong)";
  export let variant: "circled" | "cross" = "circled";
</script>

{#if variant === "circled"}
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M13.5109 18.4889L15.9998 16M15.9998 16L18.4887 13.5112M15.9998 16L13.5109 13.5112M15.9998 16L18.4887 18.4889M27.1998 16C27.1998 22.1856 22.1854 27.2 15.9998 27.2C9.81422 27.2 4.7998 22.1856 4.7998 16C4.7998 9.81446 9.81422 4.80005 15.9998 4.80005C22.1854 4.80005 27.1998 9.81446 27.1998 16Z"
      stroke={color}
      stroke-width="1.67"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
{:else}
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M12.0002 10.5857L16.9502 5.63574L18.3642 7.04974L13.4142 11.9997L18.3642 16.9497L16.9502 18.3637L12.0002 13.4137L7.05023 18.3637L5.63623 16.9497L10.5862 11.9997L5.63623 7.04974L7.05023 5.63574L12.0002 10.5857Z"
      fill="#17372F"
    />
  </svg>
{/if}
