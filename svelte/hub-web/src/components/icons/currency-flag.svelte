<script lang="ts">
  export let code: string;
</script>

<img src="/images/currency-flags/{code.toLowerCase()}.png" alt="" class="currency-flag" />

<style>
  .currency-flag {
    width: 40px;
    border-radius: 2px;
  }
</style>
