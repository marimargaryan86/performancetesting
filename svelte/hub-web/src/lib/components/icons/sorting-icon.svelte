<script lang="ts">
  import type { DirectionY } from "$lib/models/spatial";

  export let color: {
    inactive?: string;
    active?: string;
  } = {};
  export let direction: DirectionY | undefined = undefined;

  $: activeColor = color.active ?? "var(--color-common-light-strong)";
  $: inactiveColor = color.inactive ?? "var(--color-main-neutral-400)";
</script>

<svg width="14" height="14" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path
    d="M6.42424 1.97572C6.31172 1.8632 6.15911 1.79999 5.99998 1.79999C5.84085 1.79999 5.68823 1.8632 5.57571 1.97572L3.77571 3.77572C3.5414 4.01004 3.5414 4.38994 3.77571 4.62425C4.01003 4.85857 4.38992 4.85857 4.62424 4.62425L5.99998 3.24852L7.37571 4.62425C7.61003 4.85857 7.98992 4.85857 8.22424 4.62425C8.45855 4.38994 8.45855 4.01004 8.22424 3.77572L6.42424 1.97572Z"
    fill={direction === "up" ? activeColor : inactiveColor}
  />
  <path
    fill={direction === "down" ? activeColor : inactiveColor}
    d="M3.77571 7.37575C4.01003 7.14143 4.38993 7.14143 4.62424 7.37575L5.99998 8.75149L7.37571 7.37575C7.61003 7.14143 7.98992 7.14143 8.22424 7.37575C8.45855 7.61006 8.45855 7.98996 8.22424 8.22428L6.42424 10.0243C6.18992 10.2586 5.81003 10.2586 5.57571 10.0243L3.77571 8.22428C3.5414 7.98996 3.5414 7.61006 3.77571 7.37575Z"
  />
</svg>
