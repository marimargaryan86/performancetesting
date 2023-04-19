<script lang="ts">
  let className: string | undefined = undefined;

  export { className as class };
</script>

<div class="table {className ? className : ''}">
  <table><slot /></table>
</div>

<style>
  .table {
    overflow: auto;
    background-color: var(--color-main-primary-50);
    border-radius: 8px;
  }

  table {
    width: 100%;
  }
</style>
