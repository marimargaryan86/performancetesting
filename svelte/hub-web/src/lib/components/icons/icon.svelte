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
    | "calendar"
    | "car"
    | "checked"
    | "checked-circular"
    | "clock-filled"
    | "clock-outlined"
    | "close"
    | "close-circled"
    | "copy"
    | "dashboard"
    | "delete-user"
    | "download"
    | "edit"
    | "edit-user"
    | "email"
    | "flight"
    | "information"
    | "knowledge"
    | "lock"
    | "logout"
    | "password"
    | "password-circular"
    | "passenger"
    | "payment"
    | "pdf"
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
    | "swap-directions"
    | "ticket"
    | "train"
    | "user"
    | "user-circular"
    | "user-cross";

  export let size: string | undefined = undefined;
  export let color: string | undefined = undefined;

  $: mask = `url("/images/icons/${variant}.svg")`;
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
