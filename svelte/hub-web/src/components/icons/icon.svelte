<script lang="ts">
  export let variant:
    | "accounts"
    | "activity"
    | "alert-triangle"
    | "alert-disc"
    | "beneficiary"
    | "bill"
    | "bookings"
    | "bug"
    | "checked"
    | "clock-filled"
    | "clock-outlined"
    | "close"
    | "close-circled"
    | "copy"
    | "dashboard"
    | "edit"
    | "email"
    | "flight"
    | "information"
    | "knowledge"
    | "lock"
    | "logout"
    | "passenger"
    | "payment"
    | "phone"
    | "play"
    | "play-circled"
    | "plus"
    | "priority-payment"
    | "regular-payment"
    | "remove-cross"
    | "remove-trash"
    | "search"
    | "seat"
    | "ticket"
    | "download"
    | "pdf";
  export let size = "24px";
  export let color: string | undefined = undefined;

  $: mask = `url("/images/icons/${variant}.svg")`;
</script>

<div
  class="icon"
  style:mask-image={mask}
  style:-webkit-mask-image={mask}
  style:width={size}
  style:height={size}
  style:background-color={color}
/>

<style>
  .icon {
    display: inline-block;
    mask-size: contain;
    mask-repeat: no-repeat;
    mask-position: center;
    background-color: var(--color-common-light-strong);
    /* stylelint-disable property-no-vendor-prefix */
    -webkit-mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    -webkit-mask-position: center;
    /* stylelint-enable property-no-vendor-prefix */
  }
</style>
