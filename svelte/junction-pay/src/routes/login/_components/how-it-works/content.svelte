<script lang="ts">
  import { fade, fly } from "svelte/transition";

  export let section: {
    color1: string;
    color2: string;
    color3: string;
    color4: string;
    duration: number;
    items: { title: string; content?: string }[];
  };
  export let fadeDuration: number;
  export let flyDuration: number;
</script>

<div
  class="content"
  style:--color1={section.color1}
  style:--color2={section.color2}
  style:--color3={section.color3}
  style:--color4={section.color4}
  transition:fade|local={{ duration: fadeDuration }}
>
  <div
    class="wrapper"
    in:fly|local={{ duration: flyDuration, x: 400 }}
    out:fly|local={{ duration: flyDuration, x: -400 }}
  >
    <h1>How It Works</h1>

    {#each section.items as item}
      <h2>{item.title}</h2>

      {#if item.content}<p>{item.content}</p>{/if}
    {/each}
  </div>
</div>

<style>
  .content {
    align-items: center;
    background-color: var(--color-white);
    background-image: linear-gradient(
      0deg,
      var(--color1) 0.06%,
      var(--color2) 47.41%,
      var(--color3) 99.96%
    );
    display: flex;
    height: 100%;
    justify-content: center;
    left: 0;
    padding: 0 62px;
    position: absolute;
    top: 0;
  }

  .wrapper {
    background-color: var(--color-white);
    border-radius: 10px;
    box-shadow: 0 109.322px 87.4576px rgb(41 72 152 / 5%), 0 70.86px 51.22px rgb(41 72 152 / 3.8%),
      0 42.11px 27.86px rgb(41 72 152 / 3.04%), 0 21.86px 14.21px rgb(41 72 152 / 2.5%),
      0 8.9px 7.13px rgb(41 72 152 / 1.96%), 0 2.02px 3.44px rgb(41 72 152 / 1.2%);
    font-size: 14px;
    padding: 46px 36px 39px;
  }

  h1 {
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 45px;
    text-align: center;
  }

  h2 {
    align-items: center;
    display: flex;
    font-weight: 600;
  }

  h2::before {
    background-color: var(--color4);
    border-radius: 50%;
    content: "";
    display: block;
    height: 39px;
    margin-right: 31px;
    width: 39px;
  }

  p {
    color: var(--color-gray-lighter);
    display: grid;
    grid-template-columns: 70px 1fr;
    line-height: 1.58;
    min-height: 91px;
  }

  p::before {
    border-right: var(--color-gray-lighter) 1px dashed;
    content: "";
    display: block;
    height: 100%;
    width: 20px;
  }
</style>
