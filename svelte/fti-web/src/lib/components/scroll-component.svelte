<script lang="ts">
  let scrollContainer: HTMLElement;
  let index = 0;

  function getNextElementInContainerScrollLeft(): number {
    const children = scrollContainer.childNodes;
    const childDiv = Array.from(children).filter((el) => el.nodeName === "DIV") as HTMLElement[];
    const nextItem = childDiv[index + 1];
    const scrollLeft = nextItem.offsetLeft;
    return scrollLeft;
  }

  export function changePosition(event: CustomEvent): void {
    const operator = event.detail ? 1 : -1;
    const delta = operator * getNextElementInContainerScrollLeft();
    const currentScroll = scrollContainer.scrollLeft;
    const newScroll = currentScroll + delta;
    scrollContainer.scrollTo({ left: newScroll, behavior: "smooth" });
  }
</script>

<div class="scroll-container" bind:this={scrollContainer}>
  <slot />
</div>

<style>
  .scroll-container {
    position: relative;
    display: flex;
    gap: 20px;
    overflow-x: scroll;
  }

  .scroll-container::-webkit-scrollbar {
    display: none;
  }
</style>
