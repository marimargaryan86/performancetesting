export default function movable(
  node: HTMLElement,
  dragTarget?: HTMLElement,
): SvelteActionReturnType {
  let dragging = false;
  let offsetX = 0;
  let offsetY = 0;
  let dragTarget_ = dragTarget ?? node;

  function mouseDown(e: MouseEvent) {
    dragging = true;
    const { clientX, clientY } = e;

    const { offsetTop, offsetLeft } = node;

    offsetX = clientX - offsetLeft;
    offsetY = clientY - offsetTop;
  }

  function mouseUp() {
    dragging = false;
  }

  function mouseMove(e: MouseEvent) {
    if (!dragging) {
      return;
    }

    const { clientX, clientY } = e;
    const x = Math.min(Math.max(0, clientX - offsetX), window.innerWidth - node.clientWidth);
    const y = Math.min(Math.max(0, clientY - offsetY), window.innerHeight - node.clientHeight);

    node.style.left = `${x}px`;
    node.style.top = `${y}px`;
  }

  function resize(): void {
    const { offsetTop, offsetLeft, clientWidth, clientHeight } = node;
    const x = Math.min(Math.max(0, offsetLeft), window.innerWidth - clientWidth);
    const y = Math.min(Math.max(0, offsetTop), window.innerHeight - clientHeight);

    node.style.left = `${x}px`;
    node.style.top = `${y}px`;
  }

  dragTarget_.addEventListener("mousedown", mouseDown);
  document.addEventListener("mousemove", mouseMove);
  document.addEventListener("mouseup", mouseUp);
  window.addEventListener("resize", resize);

  return {
    destroy() {
      dragTarget_.removeEventListener("mousedown", mouseDown);
      document.removeEventListener("mousemove", mouseMove);
      document.removeEventListener("mouseup", mouseUp);
      window.removeEventListener("resize", resize);
    },
    update(dragTarget?: HTMLElement) {
      dragTarget_.removeEventListener("mousedown", mouseDown);
      dragTarget_ = dragTarget ?? node;
      dragTarget_.addEventListener("mousedown", mouseDown);
    },
  };
}
