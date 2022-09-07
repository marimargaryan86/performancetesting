<script lang="ts">
  export let viewMoreUrl: string | undefined = undefined;
</script>

<h2>
  <span><slot /></span>
  {#if viewMoreUrl}
    <a href={viewMoreUrl}>View all</a>
  {/if}
</h2>

<style>
  h2 {
    align-items: center;
    display: flex;
    font-size: 20px;
    justify-content: space-between;
    margin-bottom: 25px;
  }

  h2 > span {
    font-family: Raleway, Arial, Helvetica, sans-serif;
  }

  a {
    color: var(--color-orange);
    font-size: 12px;
    font-weight: 500;
    text-decoration: none;
  }

  a::after {
    border: var(--color-orange) 1px solid;
    border-width: 1px 1px 0 0;
    content: "";
    display: inline-block;
    height: 6px;
    margin-left: 5px;
    transform: translateY(-1px) rotateZ(45deg);
    width: 6px;
  }
</style>
